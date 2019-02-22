import 'whatwg-fetch';
import Cookies from 'js-cookie';

const HEADERS = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken'),
};

/* eslint-disable no-undef */
const clientRequest = (url, httpMethod, body) => window.fetch(
  url, {
    method: httpMethod,
    headers: HEADERS,
    credentials: 'same-origin',
    body: JSON.stringify(body),
  },
);

/* eslint-disable import/prefer-default-export */
export {
  clientRequest,
};
