-- Email (and optional phone push) to the admin when a new lost/found post or message comes in.
-- Uses ntfy.sh (free, no account). The topic name is private and lives only in the database.
create extension if not exists pg_net;

create or replace function public.lf_notify() returns trigger
language plpgsql security definer set search_path = public, extensions as $$
declare
  t text; m text;
begin
  if tg_table_name = 'lost_found' then
    t := 'New ' || new.kind || ' dog post waiting';
    m := coalesce(new.dog_name || ' · ', '') || new.city || '. Tap to review and approve.';
  else
    t := 'New message for a lost/found poster';
    m := 'Someone sent a message about a post. Tap to see it and forward it.';
  end if;
  perform net.http_post(
    url := 'https://ntfy.sh/',
    body := jsonb_build_object(
      'topic', 'howlback-lf-3ef6dc8085473615',
      'title', t,
      'message', m,
      'click', 'https://howlback.app/admin/',
      'email', 'hello@howlback.app',
      'tags', jsonb_build_array('dog')
    ),
    headers := '{"Content-Type": "application/json"}'::jsonb
  );
  return new;
end $$;

drop trigger if exists lf_notify_post on public.lost_found;
create trigger lf_notify_post after insert on public.lost_found
  for each row execute function public.lf_notify();

drop trigger if exists lf_notify_msg on public.lost_found_messages;
create trigger lf_notify_msg after insert on public.lost_found_messages
  for each row execute function public.lf_notify();
