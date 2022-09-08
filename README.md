# Microservice: Protein Sequence Search using Diamond

[DIAMOND](https://github.com/bbuchfink/diamond) is an alternative to BLAST for protein sequence search

## General

### Objective

This service is implemented as a RESTful API (with FastAPI), and is expected to:

- Receive a protein query sequence from the client
- Queues a job to run the query against a diamond database (built from PEP files of 100 plants of interest)
- Return top hits by their gene identifiers and its species taxid when the job is complete
- Queries and results may be removed after a week

### Limitations

- No persistence, possibility of losing query states and results after crashes in emphemeral compute instances. However, if we are planning to host this on local workstation, this should not be a problem.

### Reference

For OpenAPI documentation, refer to `/docs` path.

## Diamond database preparation

PEP fasta files are obtained for every species. The PEP files' gene identifiers are corrected to match gene identifiers from the TPM matrices used for the Plant Gene Expression Omnibus. (Refer to Omnibus Uploader docs for more details)

Diamond's `makedb` is run against the concatenated PEP files, to create a diamond protein database.

Protein sequence queries can then be made against the Diamond db.

## Deployment

This service is deployed in Google Compute Engine, exposed to the internet via nginx. This allows us to persist local result files from the searches, as compared to the ephemeral nature of Google Cloud Run service.

[Reference 1](https://dev.to/nick_langat/how-to-deploy-a-fastapi-app-to-aws-ec2-server-46d4)
[Reference 2](https://lcalcagni.medium.com/deploy-your-fastapi-to-aws-ec2-using-nginx-aa8aa0d85ec7)
