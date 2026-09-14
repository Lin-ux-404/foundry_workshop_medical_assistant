# Third-party content notice - WHO guidelines

The three PDFs downloaded into this directory by `scripts/setup/02_download_docs.py`
are publications of the **World Health Organization (WHO)**. They are not authored by the
maintainers of this repository, and they are not covered by this repository's own licence.

The PDFs themselves are not committed - they are downloaded on demand and gitignored.
This notice is committed so the terms travel with the repository.

## Licence

All three publications are released under the
**Creative Commons Attribution-NonCommercial-ShareAlike 3.0 IGO licence (CC BY-NC-SA 3.0 IGO)**.

<https://creativecommons.org/licenses/by-nc-sa/3.0/igo/>

Under this licence you may copy, redistribute and adapt the work for **non-commercial**
purposes, provided the work is appropriately cited and any adaptation is licensed under
the same or an equivalent Creative Commons licence.

## Attribution

Reproduce the WHO suggested citation whenever content from these documents is surfaced:

| Document | Suggested citation |
| --- | --- |
| HEARTS D | Diagnosis and management of type 2 diabetes (HEARTS-D). Geneva: World Health Organization; 2020 (WHO/UCN/NCD/20.1). Licence: CC BY-NC-SA 3.0 IGO. |
| Hypertension | Guideline for the pharmacological treatment of hypertension in adults. Geneva: World Health Organization; 2021. Licence: CC BY-NC-SA 3.0 IGO. |
| IPC core components | Guidelines on core components of infection prevention and control programmes at the national and acute health care facility level. Geneva: World Health Organization; 2016. Licence: CC BY-NC-SA 3.0 IGO. |

Each citation is also stored in `scripts/setup/documents.json`, written to the blob
metadata at upload time, and projected into the search index as a retrievable `citation`
field alongside `license` and `license_url`, so answers generated from the knowledge base
can carry the required attribution.

## Adaptations and disclaimer

The licence requires that adaptations carry this disclaimer:

> This is an adaptation of an original work by the World Health Organization (WHO).
> Views and opinions expressed in the adaptation are the sole responsibility of the
> author or authors of the adaptation and are not endorsed by WHO.

Answers produced by the knowledge base in these labs are generated summaries of WHO text
and should be treated as adaptations. **Nothing produced in this workshop is validated for
clinical use.**

## Non-commercial use

The NonCommercial term restricts what may be built on this content. These labs are
training material. If you reuse this pipeline for a commercial product, replace the
source documents or obtain separate permission from WHO
(<https://www.who.int/copyright>).
