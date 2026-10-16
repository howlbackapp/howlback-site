-- Extra lost/found questions.
alter table public.lost_found
  add column if not exists breed text check (char_length(breed) <= 60),
  add column if not exists age text check (char_length(age) <= 30),
  add column if not exists collar text check (collar in ('yes','no','not_sure')),
  add column if not exists tag_text text check (char_length(tag_text) <= 120),
  add column if not exists chip text check (chip in ('yes','no','not_sure')),
  add column if not exists temperament text check (temperament in ('friendly','scared','not_sure')),
  add column if not exists with_finder text check (with_finder in ('with_me','loose')),
  add column if not exists hurt text check (hurt in ('yes','no','not_sure'));

create or replace view public.lost_found_public as
  select id, created_at, kind, city, area, seen_on, dog_name, description, photo_path,
         case when show_phone then contact_phone end as phone,
         status, reviewed_at, reunited_at,
         breed, age, collar, tag_text, chip, temperament, with_finder, hurt
  from public.lost_found
  where (status = 'approved' and created_at > now() - case when kind = 'lost' then interval '60 days' else interval '30 days' end)
     or (status = 'reunited' and reunited_at > now() - interval '24 hours');
grant select on public.lost_found_public to anon, authenticated;
