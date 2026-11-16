// B5: solo se documentan excepciones que el código lanza (raise) o que el dataset declara posibles.
const { parsear, ok, excepcionesLanzadas, seccion } = require('./lib');
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r || !Array.isArray(r.excepciones)) return ok(false, 'No es JSON puro: no se puede verificar');
  const permitidas = new Set([...excepcionesLanzadas(context.vars.codigo), ...String(context.vars.excepciones_permitidas || '').split(',').map((x) => x.trim()).filter(Boolean)]);
  const citadas = [...r.excepciones.map((e) => e.tipo), ...seccion(r.docstring || '', ['Raises?', 'Excepciones'])];
  const inventadas = [...new Set(citadas.filter((e) => !permitidas.has(e)))];
  return ok(inventadas.length === 0, inventadas.length ? `Excepciones inventadas: ${inventadas.join(', ')}` : 'Sin excepciones inventadas');
};
