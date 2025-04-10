# Kardosa Project TODO List

## Core Functionality
- [x] ~~Create basic Flask backend structure~~
- [x] ~~Set up database models (User, Card, Player, Team)~~
- [x] ~~Implement user authentication~~
- [ ] Implement card collection management
- [ ] Add card trading/marketplace functionality

## Image Processing
- [x] ~~Implement binder page card extraction~~
- [x] ~~Create image splitting utility~~
- [ ] Improve card detection accuracy
- [ ] Add support for different binder/album layouts

## eBay Integration
- [x] ~~Implement eBay API client~~
- [x] ~~Create card mapping from eBay listings~~
- [x] Enhance player name matching logic
  - [x] Implement multi-strategy name matching
  - [x] Use fuzzy matching with configurable threshold
  - [x] Handle name variations (Jr., III, shortened names)
- [x] Develop comprehensive year/season extraction
  - [x] Create regex patterns for multiple season formats
  - [x] Support variations: "2024-25", "24-25", "2024"
  - [x] Build season mapping and normalization
- [ ] Advanced team identification
  - [ ] Create extensive team name/abbreviation database
  - [ ] Implement fuzzy matching for team names
  - [ ] Handle partial matches and common variations
  - [x] Extract team from multiple sources (title, card details)
- [ ] Robust card set recognition
  - [ ] Build comprehensive card set database
  - [ ] Use regex and fuzzy matching for set names
  - [ ] Normalize and standardize set name variations
  - [ ] Support partial and full set name matching
- [ ] Implement card number parsing
  - [ ] Create flexible parsing for different numbering formats
  - [ ] Handle special cases (e.g., "NNO" for No Number)
  - [ ] Support parallel/parallel variations
- [x] Implement caching for eBay API responses
  - [x] Design Caching Strategy
  - [x] Implement Caching Mechanism
  - [x] Add fallback to in-memory caching
- [x] Add error handling and logging for parsing failures
- [ ] Create configurable matching confidence levels
- [ ] Develop machine learning model for improved matching

## Player Database
- [x] ~~Create initial player database~~
- [x] ~~Add script to import current season players~~
- [ ] Implement player data update mechanism
- [ ] Add more comprehensive player metadata

## Frontend Integration
- [ ] Create React frontend
- [ ] Implement card collection view
- [ ] Add user dashboard
- [ ] Create card upload interface

## Machine Learning / Advanced Features
- [ ] Develop card value prediction model
- [ ] Implement card condition grading AI
- [ ] Create recommendation system for card collecting

## Performance and Scalability
- [ ] Optimize database queries
- [ ] Implement caching mechanisms
- [ ] Add pagination for large collections

## Security and Authentication
- [x] ~~Implement basic user authentication~~
- [ ] Add two-factor authentication
- [ ] Implement role-based access control

## Testing
- [ ] Create unit tests for backend
- [ ] Develop integration tests
- [ ] Set up continuous integration pipeline

## Deployment
- [ ] Containerize application with Docker
- [ ] Set up cloud deployment (AWS/GCP)
- [ ] Configure production environment settings

## Additional Features
- [ ] Add card grading history tracking
- [ ] Implement social sharing features
- [ ] Create price tracking for cards
- [ ] Add card condition assessment tool 