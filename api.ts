import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// 開発中はMacのローカルIPアドレスを指定します。
// iPhoneの実機から 'localhost' や '127.0.0.1' にはアクセスできません。
// ターミナルで `ifconfig | grep "inet " | grep -v 127.0.0.1` を実行してIPアドレスを確認してください。
const YOUR_MAC_IP_ADDRESS = '192.168.3.22'; // ← ここをあなたのMacのIPアドレスに書き換えてください
const API_BASE_URL = `http://${YOUR_MAC_IP_ADDRESS}:8000/api`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,

