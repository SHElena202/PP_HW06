import datetime
from unittest import TestCase

from django.urls import reverse
from django.utils import timezone

from polls.models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIn(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIn(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIn(recent_question.was_published_recently(), True)

    def create_question(question_text, days):
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.asserQuerysetEqual(response.context['latest_question_list'], [])


    def test_past_question(self):
        q = create_question(question_text='Past question.', days=-30)
        q.choice_set.create(choice_text='Choice 1', votes=0)
        q.choice_set.create(choice_text='Choice 2', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_question(self):
        q = create_question(question_text='Future question.', days=30)
        q.choice_set.create(choice_text='Choice 1', votes=0)
        q.choice_set.create(choice_text='Choice 2', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        q1 = create_question(question_text='Past question.', days=-30)
        q1.choice_set.create(choice_text='Choice 1', votes=0)
        q1.choice_set.create(choice_text='Choice 2', votes=0)
        q2 = create_question(question_text='Future question.', days=30)
        q2.choice_set.create(choice_text='Choice 1', votes=0)
        q2.choice_set.create(choice_text='Choice 2', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_question(self):
        q1 = create_question(question_text='Past question 1.', days=-30)
        q1.choice_set.create(choice_text='Choice 1', votes=0)
        q1.choice_set.create(choice_text='Choice 2', votes=0)
        q2 = create_question(question_text='Past question 2.', days=-5)
        q2.choice_set.create(choice_text='Choice 1', votes=0)
        q2.choice_set.create(choice_text='Choice 2', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question 2.>', '<Question: Past question 1.>'])

    def test_question_without_choices(self):
        q = Question.objects.create(question_text='Question without choices', pub_date=timezone.now())
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_with_one_choice(self):
        q = Question.objects.create(question_text='Question with one choice', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_with_two_choices(self):
        q = Question.objects.create(question_text='Question with two choices', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        q.choice_set.create(choice_text='Choice 2', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Question with two choices>'])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_q = create_question(question_text='Future question.', days=5)
        future_q.choice_set.create(choice_text='Choice 1', votes=0)
        future_q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:detail', args=(future_q.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_q = create_question(question_text='Past question.', days=-5)
        past_q.choice_set.create(choice_text='Choice 1', votes=0)
        past_q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:detail', args=(past_q.id,))
        response = self.client.get(url)
        self.assertContains(response, past_q.question_text)

    def test_question_with_one_choice(self):
        q = Question.objects.create(question_text='Question with one choice', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        url = reverse('polls:detail', args=(q.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_two_choices(self):
        q = Question.objects.create(question_text='Question with two choices', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:detail', args=(q.id,))
        response = self.client.get(url)
        self.assertContains(response, q.question_text)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        future_q = create_question(question_text='Future question.', days=5)
        future_q.choice_set.create(choice_text='Choice 1', votes=0)
        future_q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:results', args=(future_q.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_q = create_question(question_text='Past question.', days=-5)
        past_q.choice_set.create(choice_text='Choice 1', votes=0)
        past_q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:results', args=(past_q.id,))
        response = self.client.get(url)
        self.assertContains(response, past_q.question_text)

    def test_question_with_one_choice(self):
        q = Question.objects.create(question_text='Question with one choice', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        url = reverse('polls:results', args=(q.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_two_choices(self):
        q = Question.objects.create(question_text='Question with two choices', pub_date=timezone.now())
        q.choice_set.create(choice_text='Choice 1', votes=0)
        q.choice_set.create(choice_text='Choice 2', votes=0)
        url = reverse('polls:results', args=(q.id,))
        response = self.client.get(url)
        self.assertContains(response, q.question_text)






