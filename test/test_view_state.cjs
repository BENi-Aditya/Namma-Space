const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('apps/viewer/viewer.html', 'utf8');
function source(name) {
  const start = html.indexOf('        function ' + name + '(');
  const end = html.indexOf('\n        }', start) + 10;
  return html.slice(start,end);
}
const stored = {camera:{position:[1,2,3],quaternion:[0,0,0,1],target:[4,5,6],fov:51,near:.1,far:1234,zoom:1.2}};
const vector = () => ({fromArray(v){this.value=[...v];}});
const camera = {position:vector(), quaternion:vector(),updateProjectionMatrix(){this.updated=true;},updateMatrixWorld(){}};
const controls = {target:vector(),update(){}};
const badge = {};
const context = {availableModels:[{id:'one',viewState:stored}],activeModelId:'one',camera,orbitControls:controls,
  document:{getElementById(){return badge;}},localStorage:{getItem(){return '{"camera":"stale browser data"}';}},
  getStorageKey(){return 'legacy';},fitCameraToModel(){throw Error('Saved camera must not be replaced by auto-fit');}};
vm.createContext(context);
vm.runInContext(source('loadSavedModelState')+source('restoreCameraOrFit')+source('queueSaveState'),context);
assert.equal(context.loadSavedModelState(),stored);
context.restoreCameraOrFit();
assert.deepEqual(camera.position.value,[1,2,3]);assert.deepEqual(controls.target.value,[4,5,6]);
assert.equal(camera.fov,51);assert.equal(camera.zoom,1.2);assert.equal(camera.updated,true);
context.queueSaveState();assert.equal(badge.innerText,'UNSAVED CHANGES');assert.equal(context.loadSavedModelState(),stored);
assert.equal((html.match(/restoreCameraOrFit\(\);/g)||[]).length,2,'Both Gaussian and geometry loaders restore the saved camera');
console.log('PASS: persisted defaults override stale browser state; camera restores without auto-fit; edits do not overwrite lock.');
