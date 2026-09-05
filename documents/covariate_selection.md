# Covariate Selection Rationale

## Included in model
| Variable | Type | Rationale | Key citation(s) |
|---|---|---|---|
| Age | continuous | ... | ... |
| Sex | binary | ... | ... |
| Stage (IIIA/B/C) | categorical | ... | ... |
| Chemotherapy | binary | flagged: likely immortal time bias, see limitations | ... |
| Sidedness | binary | stage-III-specific effect direction | ... |
| Marital status | categorical | independent within-stage effect | ... |
| Race | categorical | independent effect, mechanism unclear | ... |
| Regional nodes examined | continuous | nodal harvest adequacy, independent of N-stage | ... |

## Considered, not included
| Variable | Reason excluded | Key citation(s) |
|---|---|---|
| RX Summ Surg Prim Site | near-zero variance in resected cohort; used for cohort definition instead | ... |
| Radiation recode | not standard-of-care for colon; confounded by indication | ... |
| Histologic type (mucinous/signet) | mixed evidence, low cell counts in Stage III subset — revisit if n permits | ... |
| Grade/differentiation | not in current SEER extract — flagged as limitation, candidate for re-pull | ... |
| T/N/M component fields, Regional nodes positive, SEER historic stage A | collinear with derived Stage variable | ... |

## Open questions
- Grade re-extraction decision
- Year of diagnosis as PH-assumption check item