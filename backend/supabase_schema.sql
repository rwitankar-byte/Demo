create table if not exists public.status_checks (
    id text primary key,
    client_name text not null,
    timestamp timestamptz not null default timezone('utc', now())
);

create table if not exists public.diagnoses (
    id text primary key,
    crop_name text not null,
    disease_label text not null,
    confidence double precision not null,
    severity text not null,
    visible_symptoms text not null,
    likely_cause text not null,
    treatment text not null,
    preventive_measures text not null,
    plain_language_advisory text not null,
    language text not null default 'en',
    timestamp timestamptz not null default timezone('utc', now())
);

create index if not exists diagnoses_timestamp_idx on public.diagnoses (timestamp desc);
