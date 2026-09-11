# Appointment data

The labs query a real, published dataset of medical appointment attendance. It is
third-party data from Brazil in 2016 - it is **not** data from the fictional
clinic the labs are set in, and the two should not be conflated.

- **Source:** [Medical Appointment No Shows](https://www.kaggle.com/datasets/joniarroba/noshowappointments/data)
- **Author:** Joni Hoppen
- **File:** `KaggleV2-May-2016.csv` - 110,527 rows, 14 columns, ~10.7 MB
- **Licence:** CC BY-NC-SA 4.0 - see [LICENSE.md](LICENSE.md)

The CSV is not committed to this repository. Download it from the link above and
place it here.

## Schema

The index renames the source columns. Both names are listed because the raw
headers still appear in the CSV.

| Source column | Index field | Type | Notes |
| --- | --- | --- | --- |
| `PatientId` | `patient_id` | String | Repeats across rows; a float in scientific notation |
| `AppointmentID` | `appointment_id` | String | Unique - the document key |
| `Gender` | `gender` | String | `F` / `M` |
| `ScheduledDay` | `scheduled_day` | DateTimeOffset | When the appointment was booked |
| `AppointmentDay` | `appointment_day` | DateTimeOffset | Time is always `00:00:00` |
| `Age` | `age` | Int32 | Contains at least one negative value |
| `Neighbourhood` | `neighbourhood` | String | The **clinic's** location, not the patient's |
| `Scholarship` | `scholarship` | Int32 | Enrolled in the Bolsa Família welfare programme |
| `Hipertension` | `hypertension` | Int32 | Misspelled in the source |
| `Diabetes` | `diabetes` | Int32 | |
| `Alcoholism` | `alcoholism` | Int32 | |
| `Handcap` | `handicap` | Int32 | Misspelled in the source; **0–4, not a flag** |
| `SMS_received` | `sms_received` | Int32 | Reminder sent |
| `No-show` | `no_show` | String | **Inverted** - see below |

## Hazards

These are genuine traps. Several of them produce confidently wrong answers rather
than errors, which makes them useful teaching material.

1. **`no_show` is inverted.** `"Yes"` means the patient did **not** attend.
   Filtering `no_show eq 'No'` returns people who *did* show up.
2. **Two headers are misspelled** - `Hipertension` and `Handcap`. Querying the
   correct spelling against the raw file returns nothing, with no error.
3. **`handicap` is 0–4**, not 0/1. Treating it as a boolean overcounts.
4. **`neighbourhood` is where the clinic is**, not where the patient lives. It
   does not support conclusions about patients' home areas.
5. **At least one age is negative.** It skews any unfiltered minimum or mean.
6. **`appointment_day` has no time component**, so same-day booking gaps round
   to zero and can appear negative against `scheduled_day`.
7. **`patient_id` repeats.** Rows are appointments, not people; counting rows
   over-weights frequent attenders.

## Using this responsibly

The licence is non-commercial, and this is real health data about real people.
In the labs, keep to aggregates and read-only lookups.

Do not build anything that scores, ranks, or flags individual patients by their
likelihood of missing an appointment. Beyond the ethics, the dataset cannot
support it: the strongest signals here are about clinic logistics, and a model
trained on them would mostly learn which neighbourhoods are poor.
