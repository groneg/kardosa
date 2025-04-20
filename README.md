# Kardosa - Digital Sports Card Binder

Kardosa is a mobile-friendly web application designed to be a digital binder for sports card collectors. It aims to automate the tedious process of card data entry using image recognition and provide a clean, intuitive interface for managing and viewing collections.

## Key Features

*   **Automated Card Entry:** Recognize single cards or full binder pages (9 cards) using image recognition (potentially leveraging APIs like eBay's).
*   **iPhoto-Inspired UI:** Browse card collections via a scrollable grid of images. Tap a card to view detailed information.
*   **Search & Filtering:** Easily search and filter cards based on various attributes (player, year, set, team, grade, etc.).
*   **User Authentication:** Secure user accounts to manage personal collections.
*   **Collection Sharing:** Share collections with others via usernames (future feature).
*   **Marketplace Integration:** Future integration with platforms like WhatNot for buying/selling.
*   **Focus on Speed & Ease:** Prioritize fast loading and minimal manual data entry.

## Technology Stack

*   **Frontend:** Next.js (React)
*   **Backend:** Flask (Python)
*   **Database:**
    *   Development: SQLite
    *   Production: PostgreSQL (planned migration)
*   **Image Storage:** Cloud Object Storage (e.g., AWS S3, Google Cloud Storage)
*   **Image Recognition:** Python libraries (e.g., OpenCV) and potentially external APIs.

## Getting Started

*(Instructions to be added later)*

# Trigger Vercel redeploy 