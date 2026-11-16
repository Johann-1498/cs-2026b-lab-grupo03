// B2 (aserción clave): TODOS los parámetros de la firma están documentados en `parametros`.
const { parsear, ok, parametrosReales } = require('./lib');
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r || !Array.isArray(r.parametros)) return ok(false, 'No es JSON puro: no se puede verificar');
  const doc = r.parametros.map((p) => String(p.nombre).replace(/^\*+/, ''));
  const faltan = parametrosReales(context.vars.codigo).filter((n) => !doc.includes(n));
  return ok(faltan.length === 0, faltan.length ? `Sin documentar: ${faltan.join(', ')}` : 'Todos documentados');
};
