from django.core.management.base import BaseCommand
from django.db import transaction
from contest.models import Contest, ContestProblem
from problems.models import Problem, TestCase

class Command(BaseCommand):
    help = 'Migrates problems from a finished contest to the main problem set.'

    def add_arguments(self, parser):
        # Add an argument to specify which contest to migrate
        parser.add_argument('contest_id', type=int, help='The ID of the contest to migrate.')

    def handle(self, *args, **options):
        contest_id = options['contest_id']
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Contest with ID "{contest_id}" does not exist.'))
            return

        self.stdout.write(f'Starting migration for contest: "{contest.title}"...')

        try:
            # Use a transaction to ensure that if anything fails, the database is rolled back
            with transaction.atomic():
                contest_problems = ContestProblem.objects.filter(contest=contest)
                if not contest_problems.exists():
                    self.stdout.write(self.style.WARNING('This contest has no problems to migrate.'))
                    return

                for contest_problem in contest_problems:
                    # Create a new main problem
                    main_problem = Problem.objects.create(
                        title=contest_problem.title,
                        description=contest_problem.description,
                        difficulty=contest_problem.difficulty,
                        memory_limit=256 # Or another default
                    )
                    
                    # Copy all associated test cases
                    for contest_test_case in contest_problem.test_cases.all():
                        TestCase.objects.create(
                            problem=main_problem,
                            input_data=contest_test_case.input_data,
                            output_data=contest_test_case.output_data
                        )
                    self.stdout.write(f'  - Migrated problem: "{contest_problem.title}"')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during migration: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully migrated all problems from "{contest.title}".'))