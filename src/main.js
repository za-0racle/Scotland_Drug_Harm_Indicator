import './style.css';
import './platform/style.css';
import './platform/shared.css';
import {mountPlatform} from './platform/dashboard.js';
mountPlatform(document.querySelector('#app'));
