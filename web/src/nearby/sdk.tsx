import { createRoot } from 'react-dom/client';
import Nearby, { type NearbyHost } from './Nearby';
import css from './nearby.css?inline';

export type { NearbyHost } from './Nearby';
export { default as Nearby } from './Nearby';

/** Mount one isolated feature instance. The host owns identity, API transport and savings. */
export function mountNearby(element: HTMLElement, host: NearbyHost) {
  if (element.childNodes.length || element.shadowRoot) throw new Error('Use a new empty container.');
  const shadow = element.attachShadow({mode: 'open'});
  const style = document.createElement('style'); style.textContent = css;
  const container = document.createElement('div'); shadow.append(style, container);
  const root = createRoot(container);
  let disposed = false;
  const render = (next: NearbyHost) => root.render(<Nearby host={next} />);
  render(host);
  return {
    update(next: NearbyHost) { if (disposed) throw new Error('Module was unmounted.'); render(next); },
    unmount() { if (!disposed) {root.unmount();shadow.replaceChildren();disposed = true;} },
  };
}
