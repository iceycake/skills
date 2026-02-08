#!/usr/bin/env node

import {
  createRaindrop, getRaindrop, updateRaindrop, deleteRaindrop, listRaindrops,
  listCollections, listTags, renameTag, deleteTag,
} from '../lib/api.js';

const [,, cmd, ...args] = process.argv;

function flag(name) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return undefined;
  return args[i + 1];
}

function flagList(name) {
  const v = flag(name);
  return v ? v.split(',').map(s => s.trim()) : undefined;
}

function usage() {
  console.log(`raindrop — Raindrop.io CLI

Commands:
  create  --link <url> [--title <t>] [--note <n>] [--tags <a,b>] [--collection <id>] [--excerpt <e>]
  get     <id>
  update  <id> [--title <t>] [--note <n>] [--tags <a,b>] [--collection <id>] [--link <url>] [--excerpt <e>]
  delete  <id>
  list    [collection-id] [--page <n>] [--perpage <n>] [--sort <field>]
  search  <query> [--collection <id>] [--page <n>] [--perpage <n>]
  collections
  tags    [collection-id]
  tag-rename <old> <new> [--collection <id>]
  tag-delete <name> [--collection <id>]

Env: RAINDROP_TOKEN (required)`);
}

function json(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

function printRaindrop(r) {
  const parts = [
    `[${r._id}] ${r.title || '(untitled)'}`,
    `  link: ${r.link}`,
  ];
  if (r.excerpt) parts.push(`  excerpt: ${r.excerpt}`);
  if (r.note) parts.push(`  note: ${r.note}`);
  if (r.tags?.length) parts.push(`  tags: ${r.tags.join(', ')}`);
  if (r.collection?.$id) parts.push(`  collection: ${r.collection.$id}`);
  parts.push(`  created: ${r.created}`);
  console.log(parts.join('\n'));
}

try {
  switch (cmd) {
    case 'create': {
      const link = flag('link');
      if (!link) { console.error('--link is required'); process.exit(1); }
      const res = await createRaindrop({
        link,
        title: flag('title'),
        note: flag('note'),
        tags: flagList('tags'),
        collection: flag('collection'),
        excerpt: flag('excerpt'),
      });
      printRaindrop(res.item);
      break;
    }

    case 'get': {
      const id = args[0];
      if (!id) { console.error('Usage: raindrop get <id>'); process.exit(1); }
      const res = await getRaindrop(id);
      printRaindrop(res.item);
      break;
    }

    case 'update': {
      const id = args[0];
      if (!id) { console.error('Usage: raindrop update <id> [flags]'); process.exit(1); }
      const res = await updateRaindrop(id, {
        title: flag('title'),
        note: flag('note'),
        tags: flagList('tags'),
        collection: flag('collection'),
        link: flag('link'),
        excerpt: flag('excerpt'),
      });
      printRaindrop(res.item);
      break;
    }

    case 'delete': {
      const id = args[0];
      if (!id) { console.error('Usage: raindrop delete <id>'); process.exit(1); }
      await deleteRaindrop(id);
      console.log(`Deleted raindrop ${id}`);
      break;
    }

    case 'list': {
      const colId = args[0] && !args[0].startsWith('--') ? args[0] : 0;
      const res = await listRaindrops(colId, {
        page: Number(flag('page') || 0),
        perpage: Number(flag('perpage') || 25),
        sort: flag('sort') || '-created',
      });
      if (!res.items?.length) { console.log('No raindrops found.'); break; }
      console.log(`Showing ${res.items.length} of ${res.count} raindrops:\n`);
      res.items.forEach(r => { printRaindrop(r); console.log(); });
      break;
    }

    case 'search': {
      const query = args[0];
      if (!query) { console.error('Usage: raindrop search <query>'); process.exit(1); }
      const colId = flag('collection') || 0;
      const res = await listRaindrops(colId, {
        search: query,
        page: Number(flag('page') || 0),
        perpage: Number(flag('perpage') || 25),
      });
      if (!res.items?.length) { console.log('No results.'); break; }
      console.log(`Found ${res.count} results:\n`);
      res.items.forEach(r => { printRaindrop(r); console.log(); });
      break;
    }

    case 'collections': {
      const { root, children } = await listCollections();
      const all = [...root, ...children];
      if (!all.length) { console.log('No collections.'); break; }
      all.forEach(c => console.log(`[${c._id}] ${c.title} (${c.count} items)`));
      break;
    }

    case 'tags': {
      const colId = args[0] || 0;
      const res = await listTags(colId);
      if (!res.items?.length) { console.log('No tags.'); break; }
      res.items.forEach(t => console.log(`${t._id} (${t.count})`));
      break;
    }

    case 'tag-rename': {
      const [oldName, newName] = args;
      if (!oldName || !newName) { console.error('Usage: raindrop tag-rename <old> <new>'); process.exit(1); }
      await renameTag(oldName, newName, flag('collection') || 0);
      console.log(`Renamed tag "${oldName}" → "${newName}"`);
      break;
    }

    case 'tag-delete': {
      const name = args[0];
      if (!name) { console.error('Usage: raindrop tag-delete <name>'); process.exit(1); }
      await deleteTag(name, flag('collection') || 0);
      console.log(`Deleted tag "${name}"`);
      break;
    }

    default:
      usage();
      if (cmd && cmd !== 'help' && cmd !== '--help') process.exit(1);
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
