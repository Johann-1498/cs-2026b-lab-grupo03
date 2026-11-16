// B6: `retorna` es un objeto si la función devuelve un valor y null si no devuelve nada.
const { parsear, ok, devuelveValor } = require('./lib');
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r || !('retorna' in r)) return ok(false, 'No es JSON puro: no se puede verificar');
  const debe = devuelveValor(context.vars.codigo);
  const tiene = r.retorna !== null;
  return ok(debe === tiene, `la función ${debe ? 'devuelve' : 'no devuelve'} un valor; retorna ${tiene ? 'documentado' : 'null'}`);
};
