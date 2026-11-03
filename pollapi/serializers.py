from django.db import transaction
from rest_framework import serializers

from .models import Option, Poll, Vote


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'votes']
        read_only_fields = ['votes']


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')
    my_vote = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'question', 'status', 'options', 'creator', 'my_vote', 'created_at', 'updated_at']
        read_only_fields = ['status', 'creator', 'created_at', 'updated_at']

    def get_my_vote(self, obj):
        request = self.context.get('request')
        if not (request and request.user.is_authenticated):
            return None

        prefetched = getattr(obj, '_prefetched_objects_cache', {}).get('votes')
        if prefetched is not None:
            for vote in prefetched:
                if vote.voter_id == request.user.id:
                    return vote.option_id
            return None

        vote = Vote.objects.filter(poll=obj, voter=request.user).only('option_id').first()
        return vote.option_id if vote else None

    def _option_texts(self):
        options_data = self.initial_data.get('options', [])
        if not isinstance(options_data, list) or len(options_data) < 2:
            raise serializers.ValidationError({'options': ['Must provide at least 2']})
        if len(options_data) > 5:
            raise serializers.ValidationError({'options': ['You cannot have more than 5 options']})

        texts = []
        for item in options_data:
            if isinstance(item, str):
                text = item
            elif isinstance(item, dict):
                text = item.get('text', '')
            else:
                text = ''

            if not isinstance(text, str):
                raise serializers.ValidationError({
                    'options': ['Each option must be a string or an object with text.'],
                })

            text = text.strip()
            if not text:
                raise serializers.ValidationError({'options': ['Option text cannot be blank.']})
            if len(text) > 200:
                raise serializers.ValidationError({
                    'options': ['Option text cannot be longer than 200 characters.'],
                })
            texts.append(text)
        return texts

    def create(self, validated_data):
        texts = self._option_texts()
        creator = validated_data.pop('creator', None)
        if creator is None:
            request = self.context.get('request')
            if request is None or not request.user.is_authenticated:
                raise serializers.ValidationError({'creator': ['Authentication required.']})
            creator = request.user

        with transaction.atomic():
            poll = Poll.objects.create(creator=creator, **validated_data)
            Option.objects.bulk_create([Option(poll=poll, text=text) for text in texts])
        return poll
