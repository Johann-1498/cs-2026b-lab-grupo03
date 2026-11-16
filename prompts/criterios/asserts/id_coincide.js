// A6: el historia_id de la respuesta es el de la historia analizada.
// Auto-contenida (sin require): el mismo código se puede pegar inline en casos.yaml.
const parsear = (o) => { try { const x = JSON.parse(o); return x && typeof x === 'object' && !Array.isArray(x) ? x : null; } catch (e) { return null; } };
const ok = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r) return ok(false, 'No es JSON puro');
  return ok(r.historia_id === context.vars.id, `historia_id=${r.historia_id} esperado=${context.vars.id}`);
};
