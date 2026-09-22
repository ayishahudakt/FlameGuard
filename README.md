# 🔥 FlameGuard – Intelligent Forest Monitoring System

FlameGuard is an intelligent forest monitoring system designed to support the detection and monitoring of **forest fires, wildlife, and human intrusion**.

The project combines a Django-based web backend, Flutter mobile application, computer vision, and AI-based detection to support forest monitoring and incident reporting.

---

## 🎯 Project Overview

Forest environments require continuous monitoring to identify potential fire incidents, wildlife activity, and unauthorized human presence.

FlameGuard brings together web-based management modules, a mobile application, and camera-based AI processing into a single monitoring system.

---

## 🚀 Key Features

### 🔥 Fire Detection
- Processes camera input for fire-related detection.
- Uses computer vision techniques for fire detection.
- Generates alerts for detected fire incidents.

### 🐘 Wildlife Detection
- Uses AI-based object detection for identifying wildlife.
- Provides animal-related information through the system.

### 🚶 Human Intrusion Detection
- Detects human presence in monitored areas.
- Supports monitoring of possible unauthorized intrusion.

### 🔔 Alerts & Notifications
- Provides alerts for detected incidents.
- Stores incident information such as location and time.
- Allows users and forest officers to view relevant notifications.

### 👨‍💼 Admin Module
- Manage forest divisions.
- Manage forest stations.
- Manage animals.
- Manage forest officers.
- Manage notifications.
- Manage system information.

### 👮 Forest Officer Module
- View fire detection alerts.
- Submit reports.
- Submit complaints.
- View complaint replies.

### 📱 User Module
- User registration and login.
- Search and view animals.
- Send complaints and view replies.
- View fire detection alerts.
- Receive notifications.

### 📷 Camera & AI Module
- Camera interfacing.
- Fire detection.
- Wildlife detection.
- Human intrusion detection.
- AI-based image processing.

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │     FlameGuard      │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
      │    Admin    │        │   Officer   │        │    User     │
      │   Module    │        │   Module    │        │   Module    │
      └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Django Backend   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Camera / AI Module │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                 🔥 Fire        🐘 Wildlife      🚶 Human
                 Detection      Detection        Detection
