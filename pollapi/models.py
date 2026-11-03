from django.contrib.auth.models import User
from django.db import models


class Poll(models.Model):
    # Only these two words are allowed: "open" or "closed".
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    question = models.CharField(max_length=200)
    # If this user is deleted, their polls are deleted too.
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question} ({self.status})"


class Option(models.Model):
    # This link lets us write poll.options to get every choice.
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    # How many people picked this choice. It starts at 0.
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.poll.question})"


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='vote_records')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # The same person cannot vote twice on the same poll.
        unique_together = ('poll', 'voter')

    def __str__(self):
        return f"{self.voter.username} voted for {self.option.text} in {self.option.poll.question}"
