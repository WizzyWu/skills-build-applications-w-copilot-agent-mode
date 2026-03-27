from django.core.management.base import BaseCommand
from octofit_tracker.models import User, Team, Activity, Workout, LeaderboardEntry
from django.conf import settings
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        # Delete existing data in correct order and clear M2M
        for obj in Activity.objects.all():
            if obj.id:
                obj.delete()
        for obj in LeaderboardEntry.objects.all():
            if obj.id:
                obj.delete()
        for workout in Workout.objects.all():
            if workout.id:
                workout.suggested_for.clear()
                workout.delete()
        for team in Team.objects.all():
            if team.id:
                team.members.clear()
                team.delete()
        for obj in User.objects.all():
            if obj.id:
                obj.delete()

        # Create users
        marvel_heroes = [
            {'username': 'ironman', 'email': 'ironman@marvel.com'},
            {'username': 'captainamerica', 'email': 'cap@marvel.com'},
            {'username': 'spiderman', 'email': 'spiderman@marvel.com'},
        ]
        dc_heroes = [
            {'username': 'batman', 'email': 'batman@dc.com'},
            {'username': 'superman', 'email': 'superman@dc.com'},
            {'username': 'wonderwoman', 'email': 'wonderwoman@dc.com'},
        ]
        users = []
        for hero in marvel_heroes + dc_heroes:
            user = User.objects.create_user(username=hero['username'], email=hero['email'], password='password')
            users.append(user)

        # Create teams
        marvel_team = Team.objects.create(name='Marvel')
        dc_team = Team.objects.create(name='DC')
        marvel_team.members.set(users[:3])
        dc_team.members.set(users[3:])

        # Create workouts
        workout1 = Workout.objects.create(name='Super Strength', description='Strength training for heroes')
        workout2 = Workout.objects.create(name='Agility Training', description='Agility and speed drills')
        workout1.suggested_for.set(users[:3])
        workout2.suggested_for.set(users[3:])

        # Create activities
        Activity.objects.create(user=users[0], activity_type='Running', duration=30, calories_burned=300)
        Activity.objects.create(user=users[3], activity_type='Flying', duration=45, calories_burned=500)

        # Create leaderboard entries
        LeaderboardEntry.objects.create(user=users[0], score=1000, rank=1)
        LeaderboardEntry.objects.create(user=users[3], score=950, rank=2)


        # Ensure unique index on email using pymongo
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'], settings.DATABASES['default']['CLIENT']['port'])
        db = client[settings.DATABASES['default']['NAME']]
        db.users.create_index('email', unique=True)

        self.stdout.write(self.style.SUCCESS('octofit_db database populated with test data.'))
