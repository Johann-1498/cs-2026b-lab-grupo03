// A2: si la historia es válida (invest_ok = true) debe haber >= 1 escenario de
// éxito y >= 1 de error o borde. Si la historia se rechaza, esta aserción no aplica.
// Auto-contenida (sin require): el mismo código se puede pegar inline en casos.yaml.
const parsear = (o) => { try { const x = JSON.parse(o); return x && typeof x === 'object' && !Array.isArray(x) ? x : null; } catch (e) { return null; } };
const ok = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });
module.exports = (output) => {
  const r = parsear(output);
  if (!r) return ok(false, 'No es JSON puro: no se puede verificar');
  if (r.invest_ok === false) return ok(true, 'Historia rechazada: no aplica');
  const esc = Array.isArray(r.escenarios) ? r.escenarios : [];
  const exito = esc.some((e) => e.tipo === 'exito');
  const falla = esc.some((e) => e.tipo === 'error' || e.tipo === 'borde');
  return ok(exito && falla, `exito=${exito} error/borde=${falla}`);
};
