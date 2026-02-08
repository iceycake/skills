const BASE = 'https://api.raindrop.io/rest/v1';

function token() {
  const t = process.env.RAINDROP_TOKEN;
  if (!t) {
    console.error('Error: RAINDROP_TOKEN environment variable is not set');
    process.exit(1);
  }
  return t;
}

function headers() {
  return {
    'Authorization': `Bearer ${token()}`,
    'Content-Type': 'application/json',
  };
}

async function request(method, path, body) {
  const opts = { method, headers: headers() };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    const msg = data.errorMessage || data.error || res.statusText;
    throw new Error(`${res.status} ${msg}`);
  }
  return data;
}

// --- Raindrops ---

export async function createRaindrop({ link, title, note, tags, collection, excerpt }) {
  const body = { link, pleaseParse: {} };
  if (title) body.title = title;
  if (note) body.note = note;
  if (excerpt) body.excerpt = excerpt;
  if (tags?.length) body.tags = tags;
  if (collection) body.collection = { $id: Number(collection) };
  return request('POST', '/raindrop', body);
}

export async function getRaindrop(id) {
  return request('GET', `/raindrop/${id}`);
}

export async function updateRaindrop(id, fields) {
  const body = {};
  if (fields.title) body.title = fields.title;
  if (fields.note !== undefined) body.note = fields.note;
  if (fields.excerpt !== undefined) body.excerpt = fields.excerpt;
  if (fields.tags) body.tags = fields.tags;
  if (fields.collection) body.collection = { $id: Number(fields.collection) };
  if (fields.important !== undefined) body.important = fields.important;
  if (fields.link) body.link = fields.link;
  return request('PUT', `/raindrop/${id}`, body);
}

export async function deleteRaindrop(id) {
  return request('DELETE', `/raindrop/${id}`);
}

export async function listRaindrops(collectionId = 0, { page = 0, perpage = 25, sort = '-created', search } = {}) {
  const params = new URLSearchParams({ page, perpage, sort });
  if (search) params.set('search', search);
  return request('GET', `/raindrops/${collectionId}?${params}`);
}

// --- Collections ---

export async function listCollections() {
  const [root, children] = await Promise.all([
    request('GET', '/collections'),
    request('GET', '/collections/childrens'),
  ]);
  return { root: root.items || [], children: children.items || [] };
}

// --- Tags ---

export async function listTags(collectionId = 0) {
  return request('GET', `/tags/${collectionId}`);
}

export async function renameTag(oldName, newName, collectionId = 0) {
  return request('PUT', `/tags/${collectionId}`, {
    tags: [oldName],
    replace: newName,
  });
}

export async function deleteTag(tagName, collectionId = 0) {
  return request('DELETE', `/tags/${collectionId}`, {
    tags: [tagName],
  });
}
