from django.db import IntegrityError, transaction
from django.db.models import F, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Option, Poll, Vote
from .permissions import IsPollCreator
from .serializers import PollSerializer


class PollPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # user can ask for more items with ?page_size=
    max_page_size = 100  # never return more than 100 items on one page


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.select_related('creator').order_by('-created_at')
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated, IsPollCreator]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']  # example: /api/polls/?status=open
    pagination_class = PollPagination

    def get_queryset(self):
        votes = Vote.objects.all()
        user = getattr(self.request, 'user', None)
        
        # Load only this person's vote, so we can show which choice they picked.
        if user and user.is_authenticated:
            votes = votes.filter(voter=user)
        return super().get_queryset().prefetch_related(
            'options',
            Prefetch('votes', queryset=votes),
        )

    def perform_create(self, serializer):
        # The person who is logged in is saved as the creator.
        serializer.save(creator=self.request.user)

    def destroy(self, request, *args, **kwargs):
        poll = self.get_object()
        poll_id = poll.id
        self.perform_destroy(poll)
        # 200 is used because a 204 response is not allowed to include a message.
        return Response(
            {'detail': 'Poll deleted successfully', 'poll_id': poll_id},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], url_path='vote')
    def vote(self, request, pk=None):
        poll = self.get_object()

        if poll.status != 'open':
            return Response({'detail': 'Poll is not open for voting'}, status=status.HTTP_400_BAD_REQUEST)

        option_id = request.data.get('option')
        if not option_id:
            return Response({'detail': 'Option ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            option = Option.objects.get(id=option_id, poll=poll)
        except (Option.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Option does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if Vote.objects.filter(poll=poll, voter=request.user).exists():
            return Response(
                {'detail': 'You have already voted for this poll'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                Vote.objects.create(poll=poll, option=option, voter=request.user)
                # Add 1 to the choice's vote count inside the database.
                Option.objects.filter(pk=option.pk).update(votes=F('votes') + 1)
        except IntegrityError:
            # This happens if the same person sends two votes at the same time.
            return Response(
                {'detail': 'You have already voted for this poll'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'detail': 'Vote successful',
                'poll_id': poll.id,
                'option_id': option.id,
                'option_text': option.text,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        poll = self.get_object()
        if poll.status == 'closed':
            return Response({'detail': 'Poll is already closed'}, status=status.HTTP_400_BAD_REQUEST)

        poll.status = 'closed'
        poll.save(update_fields=['status', 'updated_at'])  # only change the status and the update time
        return Response(self.get_serializer(poll).data)

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        poll = self.get_object()
        options = list(poll.options.all())
        total_votes = sum(opt.votes for opt in options)

        results_data = []
        for opt in options:
            # Turn the votes into a percentage, such as 50.0 for half the votes.
            percentage = round((opt.votes / total_votes) * 100, 2) if total_votes else 0
            results_data.append({
                'option_id': opt.id,
                'option_text': opt.text,
                'votes': opt.votes,
                'percentage': percentage,
            })

        return Response(
            {
                'poll_id': poll.id,
                'question': poll.question,
                'total_votes': total_votes,
                'results': results_data,
            },
            status=status.HTTP_200_OK,
        )
