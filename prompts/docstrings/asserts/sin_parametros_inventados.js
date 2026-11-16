// B3 (aserción clave): NO se documentan parámetros que la función no tiene (p. ej. `self`).
const { parsear, ok, parametrosReales } = require('./lib');
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r || !Array.isArray(r.parametros)) return ok(false, 'No es JSON puro: no se puede verificar');
  const reales = parametrosReales(context.vars.codigo);
  const sobran = r.parametros.map((p) => String(p.nombre).replace(/^\*+/, '')).filter((n) => !reales.includes(n));
  return ok(sobran.length === 0, sobran.length ? `Parámetros inexistentes: ${sobran.join(', ')}` : 'Ninguno inventado');
};
