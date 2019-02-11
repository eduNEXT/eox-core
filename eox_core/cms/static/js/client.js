import Cookies from 'js-cookie';

const HEADERS = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken'),
};

const clientRequest = (url, method, body) => fetch(
  url, {
    method: method,
    headers: HEADERS,
    credentials: 'same-origin',
    body: JSON.stringify(body)
  }
);

export {
  clientRequest
}
