\# Contributing



\## Branches



`main` is the stable integrated branch.



All development must happen on short-lived feature or fix branches.



Examples:



\- `feature/task-api`

\- `feature/action-graph`

\- `feature/frontend-dashboard`

\- `fix/task-validation`

\- `infra/docker-setup`

\- `docs/repository-workflow`



Do not create permanent personal branches.



\## Development Workflow



1\. Update your local `main`.

2\. Create a new branch for the task.

3\. Make only the changes related to that task.

4\. Test the changes locally.

5\. Commit with a clear message.

6\. Push the branch to GitHub.

7\. Open a Pull Request into `main`.

8\. Get at least one teammate approval.

9\. Resolve review conversations.

10\. Ensure the latest changes are reviewed.

11\. Squash-merge the Pull Request.

12\. Delete the feature branch.

13\. Update your local `main`.



\## Rules



\- Never push directly to `main`.

\- Never force-push to `main`.

\- Keep Pull Requests focused on one logical change.

\- Do not mix unrelated changes in the same Pull Request.

\- Communicate before changing shared architectural files.

\- Coordinate database schema and Alembic migration changes.

\- Coordinate API contract changes.

\- Never commit `.env` files, secrets, virtual environments, generated files, or dependency folders.



\## Shared Architecture



The repository structure is the common project structure for all team members.



Ownership means responsibility for maintaining and reviewing an area. It does not prevent another team member from contributing to that area when required.



\## Database Changes



Database schema changes must be coordinated before modifying the shared schema.



Alembic migrations must be reviewed carefully before merging.



\## API Changes



Changes to API endpoints, request schemas, response schemas, or API behavior must be communicated to affected team members.



Frontend and AI-engine dependencies on API contracts must be updated when necessary.

