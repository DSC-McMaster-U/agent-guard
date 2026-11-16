# Security

## Report a vulnerability privately

If you find a possible security problem, send a direct message to the Project
Lead, Aryan (@rinnegannn on GitHub), through the project Discord. This is the
team's reporting route; do not open a public GitHub issue or PR containing an
unreviewed vulnerability or sensitive details.

Describe what happened, the affected version or commit, and how to reproduce it
with fictional data. Remove credentials and personal information from logs or
screenshots. The Lead will coordinate investigation, a fix, and any public
explanation after reviewing the report. Do not test against systems or accounts
you do not have permission to use.

## Use fictional data

Use made-up addresses, names, message contents, and clearly fake keys in
`.env.example`, screenshots, tests, benchmark fixtures, and documentation. Use
reserved example domains such as `example.com`; never include real customer data.

Keep actual passwords, API keys, and tokens in your local environment or ignored
`.env` file. Before committing, check the staged diff for secrets. An ignored
file does not protect a secret that was already committed.

## If a secret is accidentally committed

1. Tell the Project Lead privately right away. Do not paste the secret into a
   public issue, PR, or Discord channel.
2. Revoke or rotate the credential with its provider so the old value no longer
   works. Treat it as exposed even if the commit has not been merged.
3. Remove the value from the working files and replace examples with fictional
   data. Work with the Lead to remove it from repository history where necessary;
   deleting the latest copy alone does not remove earlier commits. Coordinate
   any history rewrite before changing shared branches.

Changing Git history cannot revoke a credential or erase copies already taken.
The Lead will help assess any further response needed.
