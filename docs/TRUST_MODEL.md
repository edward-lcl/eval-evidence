# Trust and physical-verification model

## v0.1 trust boundary

Eval Evidence trusts the local caller to select a stable run directory. It validates
JSON contracts, canonical bundle identity, and referenced local bytes. It does not
isolate an actively mutating filesystem, authenticate a runner, observe provider-side
state, or establish that a verifier measured the intended construct.

Threats addressed:

- accidental or malicious post-run file mutation;
- textual path traversal and symlink escape;
- omitted instrument fields being mistaken for known values;
- a reported reward being silently represented as independent correctness evidence;
- adapter ambiguity and malformed archive entries.

Threats not addressed:

- compromised runner or operating system;
- concurrent time-of-check/time-of-use mutation;
- fabricated source artifacts hashed consistently by an attacker;
- bundle claims edited and then re-digested by an attacker (the result is internally
  valid because a content digest is not an authenticated signature);
- key compromise, reviewer impersonation, or physical sensor fraud;
- confidentiality of the source files (the bundle hashes them but does not encrypt them);
- resource exhaustion from extremely large but syntactically valid JSON or referenced files.

## Gate before signing

`attestation.signature` is null in v0.1. A signing profile must separately specify:

1. signer role and identity (lab runner, benchmark operator, independent facility);
2. exact digest and claim scope;
3. key issuance, rotation, revocation, and timestamp semantics;
4. replay protection and run identity;
5. which instrument and physical facts the signer directly observed;
6. privacy/redaction behavior;
7. verification policy when signatures or fields are absent.

Signing authenticates a signer and scoped statement; it does not make the statement
true. Hardware roots, isolated runners, or physical-verification facilities can later
fill this layer without changing the v0.1 evidence categories. No hosted registry or
global trust root is implied.
