import './style.css';
import './platform/style.css';
import {mountPlatform} from './platform/dashboard.js';
mountPlatform(document.querySelector('#app'));
