# Suppression

Who never gets handed to sales. Check this file before any handoff. Each rule has a key so a script can apply it and a disqualified row says why.

| Rule key | Matches | Why | Source of the list | Refreshed |
|---|---|---|---|---|
| `self` | the company's own domains | | | |
| `customer` | current customers | expansion has its own motion | {CRM export, owner only} | {weekly} |
| `partner_or_vendor` | partners, resellers, vendors | do not prospect | | |
| `competitor_or_builder` | rivals and companies building the same thing | | `competitors/` | |
| `under_floor` | below the size floor in `icp.md` | anti-ICP | | |
| `do_not_contact` | anyone who asked not to be contacted | legal and trust | {private list, never in git} | on every send |
| `data_error` | dead domains, duplicates, acquired companies, parent brands | | | |

A suppressed row stays in the list with `exclusion_reason` set, so nobody researches it again.
