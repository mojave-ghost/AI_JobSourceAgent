# UML Diagrams - Mermaid Format
## AI Job Source Agent

**Note:** These diagrams render directly in GitHub, GitLab, and compatible markdown viewers.

---

## DIAGRAM 1: Complete Class Diagram

```mermaid
classDiagram
    %% ============ INFRASTRUCTURE ============
    class Configuration {
        -string apifyToken
        -string anthropicApiKey
        -List~string~ careerPaths
        -List~string~ careerKeywords
        -int maxClaudeCalls
        -int requestTimeout
        -int browserTimeout
        -string outputDir
        +loadFromEnv() void
        +validate() bool
        +get(key) Any
    }

    class Logger {
        -string logFile
        -string logLevel
        -List~Dict~ logs
        +info(message) void
        +error(message, exception) void
        +warning(message) void
        +saveLogs() void
    }

    class URLValidator {
        -int timeout
        -string userAgent
        +isValid(url) bool
        +normalize(url) string
        +makeAbsolute(base, relative) string
        -checkStatus(url) int
    }

    %% ============ DATA MODELS ============
    class CompanyData {
        +string companyName
        +string companyUrl
        +string linkedinJobUrl
        +string jobTitle
        +toDict() Dict
        +validateUrl() bool
    }

    class JobSourceResult {
        +string companyName
        +string careerPageUrl
        +string openPositionUrl
        +datetime timestamp
        +int sourceTier
        +float processingTime
        +toDict() Dict
        +validate() bool
        +repr() string
    }

    class ExecutionStatistics {
        +int totalProcessed
        +int successful
        +int failed
        +int tier1Success
        +int tier2Success
        +int tier3Success
        +int claudeApiCalls
        +int linkedinApiCalls
        +float totalProcessingTime
        +datetime startTime
        +datetime endTime
        +incrementSuccess(tier) void
        +incrementFailure() void
        +calculateSuccessRate() float
        +calculateHeuristicSuccessRate() float
        +toDict() Dict
        +getSummary() string
    }

    %% ============ CORE COMPONENTS ============
    class LinkedInFetcher {
        -string apiToken
        -string baseUrl
        -int maxItems
        -int requestTimeout
        -int apiCallsMade
        -float monthlyBudget
        +fetchJobListings(url, limit) List~Dict~
        +extractCompanyData(response) List~CompanyData~
        +handleRateLimit(response) bool
        +validateApiResponse(response) bool
        -makeApiRequest(endpoint, params) Dict
        -trackApiCost(items) void
    }

    class CareerPageFinder {
        -List~string~ commonPaths
        -List~string~ careerKeywords
        -int requestTimeout
        -int maxRetries
        -int tier1SuccessCount
        -int tier2SuccessCount
        -int tier3SuccessCount
        +findCareerPage(companyUrl) string
        +findViaDirectPaths(companyUrl) string
        +scrapeHomepage(companyUrl) string
        +checkFooterNav(soup) string
        +makeAbsoluteUrl(base, relative) string
        +validateUrl(url) bool
        -matchesCareerKeyword(text, url) bool
        -isValidCareerPage(url, content) bool
    }

    class ClaudeFallback {
        -string apiKey
        -string model
        -int maxTokens
        -int callsThisMonth
        -int maxCallsPerMonth
        -float monthlyBudget
        +findCareerPageAi(companyUrl) string
        +checkMonthlyLimit() bool
        +incrementCallCounter() void
        -buildPrompt(companyUrl) string
        -parseClaudeResponse(response) string
    }

    class PositionExtractor {
        -int browserTimeout
        -int pageLoadTimeout
        -List~string~ jobSelectors
        -bool headless
        -BrowserContext browserContext
        +extractFirstPosition(careerPageUrl) string
        +navigateToPage(url) Page
        +findJobLinks(page) List~string~
        +makeAbsoluteUrl(base, jobUrl) string
        -initializeBrowser() Browser
        -waitForContent(page) void
        -extractJobUrl(element) string
    }

    class OutputManager {
        -string outputDir
        -string filenameTemplate
        -List~JobSourceResult~ results
        -ExecutionStatistics statistics
        +addResult(result) void
        +saveToJson(filename) string
        +generateFilename() string
        -formatOutput() Dict
        -ensureOutputDir() void
    }

    class JobSourcePipeline {
        -Configuration config
        -LinkedInFetcher linkedinFetcher
        -CareerPageFinder careerFinder
        -ClaudeFallback claudeFallback
        -PositionExtractor positionExtractor
        -OutputManager outputManager
        -ExecutionStatistics statistics
        -Logger logger
        +run(linkedinUrl, maxCompanies) void
        +processSingleCompany(company) JobSourceResult
        +handleError(error, company) void
        -initializeComponents() void
        -validateInputs(url, max) bool
        -printProgress(current, total) void
    }

    %% ============ RELATIONSHIPS ============
    
    %% Composition - Pipeline owns components
    JobSourcePipeline *-- "1" Configuration : owns
    JobSourcePipeline *-- "1" LinkedInFetcher : owns
    JobSourcePipeline *-- "1" CareerPageFinder : owns
    JobSourcePipeline *-- "1" ClaudeFallback : owns
    JobSourcePipeline *-- "1" PositionExtractor : owns
    JobSourcePipeline *-- "1" OutputManager : owns
    JobSourcePipeline *-- "1" ExecutionStatistics : owns
    JobSourcePipeline *-- "1" Logger : owns

    %% Composition - OutputManager contains
    OutputManager *-- "0..*" JobSourceResult : contains
    OutputManager *-- "1" ExecutionStatistics : contains

    %% Dependencies - use Configuration
    LinkedInFetcher ..> Configuration : uses
    CareerPageFinder ..> Configuration : uses
    ClaudeFallback ..> Configuration : uses
    PositionExtractor ..> Configuration : uses
    OutputManager ..> Configuration : uses

    %% Dependencies - use Logger
    LinkedInFetcher ..> Logger : logs to
    CareerPageFinder ..> Logger : logs to
    ClaudeFallback ..> Logger : logs to
    PositionExtractor ..> Logger : logs to
    OutputManager ..> Logger : logs to

    %% Dependencies - use URLValidator
    CareerPageFinder ..> URLValidator : uses
    PositionExtractor ..> URLValidator : uses

    %% Association - CareerPageFinder fallback
    CareerPageFinder --> "0..1" ClaudeFallback : fallback to

    %% Association - Data production
    LinkedInFetcher --> "1..*" CompanyData : produces
    JobSourcePipeline --> "20..50" CompanyData : processes
    JobSourcePipeline --> "0..*" JobSourceResult : creates

    %% Association - Statistics updates
    LinkedInFetcher --> ExecutionStatistics : updates
    CareerPageFinder --> ExecutionStatistics : updates
    ClaudeFallback --> ExecutionStatistics : updates
```

---

## DIAGRAM 2: Simplified Relationship Focus

```mermaid
graph TB
    subgraph "Orchestration"
        Pipeline[JobSourcePipeline]
    end

    subgraph "Data Acquisition"
        LinkedIn[LinkedInFetcher]
    end

    subgraph "Career Discovery - 3 Tier Strategy"
        Finder[CareerPageFinder]
        Claude[ClaudeFallback]
        Validator[URLValidator]
    end

    subgraph "Position Extraction"
        Extractor[PositionExtractor]
    end

    subgraph "Output"
        Output[OutputManager]
    end

    subgraph "Data Models"
        Company[CompanyData]
        Result[JobSourceResult]
        Stats[ExecutionStatistics]
    end

    subgraph "Infrastructure"
        Config[Configuration]
        Log[Logger]
    end

    %% Main flow
    Pipeline -->|owns 1| LinkedIn
    Pipeline -->|owns 1| Finder
    Pipeline -->|owns 1| Claude
    Pipeline -->|owns 1| Extractor
    Pipeline -->|owns 1| Output
    Pipeline -->|owns 1| Config
    Pipeline -->|owns 1| Log
    Pipeline -->|owns 1| Stats

    %% Data flow
    LinkedIn -->|produces 1..*| Company
    Pipeline -->|processes 20..50| Company
    Pipeline -->|creates 0..*| Result
    Output -->|contains 0..*| Result
    Output -->|contains 1| Stats

    %% Dependencies
    Finder -.->|fallback 0..1| Claude
    Finder -.->|uses 1| Validator
    Extractor -.->|uses 1| Validator

    LinkedIn -.->|updates| Stats
    Finder -.->|updates| Stats
    Claude -.->|updates| Stats

    %% Infrastructure dependencies
    LinkedIn -.->|uses| Config
    Finder -.->|uses| Config
    Claude -.->|uses| Config
    Extractor -.->|uses| Config

    LinkedIn -.->|logs to| Log
    Finder -.->|logs to| Log
    Claude -.->|logs to| Log
    Extractor -.->|logs to| Log
    Output -.->|logs to| Log

    classDef composition fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    classDef association fill:#ffe1e1,stroke:#cc0000,stroke-width:2px
    classDef dependency fill:#f0f0f0,stroke:#666,stroke-width:1px,stroke-dasharray: 5 5
    
    class Pipeline,LinkedIn,Finder,Claude,Extractor,Output composition
    class Company,Result,Stats association
    class Config,Log,Validator dependency
```

---

## DIAGRAM 3: Sequence Diagram - Main Flow

```mermaid
sequenceDiagram
    actor User
    participant Pipeline as JobSourcePipeline
    participant LinkedIn as LinkedInFetcher
    participant Finder as CareerPageFinder
    participant Claude as ClaudeFallback
    participant Extractor as PositionExtractor
    participant Output as OutputManager
    participant Stats as ExecutionStatistics

    User->>Pipeline: run(linkedin_url, max=50)
    activate Pipeline
    
    Pipeline->>Stats: start_time = now()
    
    %% LinkedIn Data Acquisition
    Pipeline->>LinkedIn: fetch_job_listings(url, 50)
    activate LinkedIn
    LinkedIn->>LinkedIn: _make_api_request()
    LinkedIn->>Stats: linkedin_api_calls++
    LinkedIn-->>Pipeline: List[CompanyData] (1..50)
    deactivate LinkedIn

    %% Process each company
    loop for each company [20..50]
        Pipeline->>Pipeline: process_single_company(company)
        
        %% Tier 1 & 2
        Pipeline->>Finder: find_career_page(company_url)
        activate Finder
        
        alt Tier 1: Direct paths (80%)
            Finder->>Finder: find_via_direct_paths()
            Finder->>Stats: tier1_success++
            Finder-->>Pipeline: career_url
        else Tier 2: Homepage scraping (15%)
            Finder->>Finder: scrape_homepage()
            Finder->>Stats: tier2_success++
            Finder-->>Pipeline: career_url
        else Tier 3: Claude API (5%)
            Finder->>Claude: find_career_page_ai(url)
            activate Claude
            
            alt Monthly limit OK
                Claude->>Claude: API call to Anthropic
                Claude->>Stats: tier3_success++
                Claude->>Stats: claude_api_calls++
                Claude-->>Finder: career_url
            else Limit reached
                Claude-->>Finder: None
            end
            deactivate Claude
            
            Finder-->>Pipeline: career_url or None
        end
        deactivate Finder

        alt career_url found
            Pipeline->>Extractor: extract_first_position(career_url)
            activate Extractor
            Extractor->>Extractor: navigate_to_page()
            Extractor->>Extractor: find_job_links()
            Extractor-->>Pipeline: position_url
            deactivate Extractor

            alt position_url found
                Pipeline->>Pipeline: create JobSourceResult
                Pipeline->>Output: add_result(result)
                Output->>Stats: successful++
            else No position
                Pipeline->>Stats: failed++
            end
        else No career page
            Pipeline->>Stats: failed++
        end
    end

    %% Save results
    Pipeline->>Stats: end_time = now()
    Pipeline->>Output: save_to_json()
    activate Output
    Output->>Output: generate_filename()
    Output->>Output: _format_output()
    Output-->>Pipeline: filename
    deactivate Output

    Pipeline-->>User: Execution complete
    deactivate Pipeline
```

---

## DIAGRAM 4: Career Finder State Machine

```mermaid
stateDiagram-v2
    [*] --> Tier1_DirectPaths

    state Tier1_DirectPaths {
        [*] --> TestingPaths
        TestingPaths --> Success_T1 : Path found (80%)
        TestingPaths --> Failed_T1 : All paths exhausted
    }

    Tier1_DirectPaths --> ReturnURL_T1 : success
    Tier1_DirectPaths --> Tier2_HomepageScraping : failed

    state Tier2_HomepageScraping {
        [*] --> ScrapingHomepage
        ScrapingHomepage --> ExtractingLinks
        ExtractingLinks --> MatchingKeywords
        MatchingKeywords --> Success_T2 : Match found (15%)
        MatchingKeywords --> Failed_T2 : No matches
    }

    Tier2_HomepageScraping --> ReturnURL_T2 : success
    Tier2_HomepageScraping --> Tier3_ClaudeAPI : failed

    state Tier3_ClaudeAPI {
        [*] --> CheckingLimit
        CheckingLimit --> CallingAPI : limit OK (max 50/month)
        CheckingLimit --> LimitExceeded : limit exceeded
        CallingAPI --> ParsingResponse
        ParsingResponse --> Success_T3 : URL extracted (5%)
        ParsingResponse --> Failed_T3 : Invalid response
    }

    Tier3_ClaudeAPI --> ReturnURL_T3 : success
    Tier3_ClaudeAPI --> ReturnNone : failed

    ReturnURL_T1 --> [*]
    ReturnURL_T2 --> [*]
    ReturnURL_T3 --> [*]
    ReturnNone --> [*]

    note right of Tier1_DirectPaths
        FREE - 80% coverage
        /careers, /jobs, etc.
    end note

    note right of Tier2_HomepageScraping
        FREE - 15% coverage
        BeautifulSoup scraping
    end note

    note right of Tier3_ClaudeAPI
        PAID - 5% coverage
        $0.30-0.40 per call
        Max 50 calls/month
    end note
```

---

## DIAGRAM 5: Data Flow Diagram

```mermaid
graph LR
    subgraph Input
        User[User Input:<br/>LinkedIn URL]
    end

    subgraph "Data Acquisition Layer"
        LinkedIn[LinkedInFetcher<br/>API Call]
        CompanyData[(CompanyData<br/>1..50 records)]
    end

    subgraph "Processing Layer"
        Finder[CareerPageFinder<br/>3-Tier Strategy]
        Claude[ClaudeFallback<br/>Tier 3]
        Extractor[PositionExtractor<br/>Playwright]
    end

    subgraph "Data Collection"
        Results[(JobSourceResult<br/>0..50 records)]
        Stats[(ExecutionStatistics<br/>1 record)]
    end

    subgraph Output
        JSON[JSON File<br/>job_sources_YYYY-MM-DD.json]
    end

    %% Flow
    User -->|1 URL| LinkedIn
    LinkedIn -->|produces| CompanyData
    CompanyData -->|20..50| Finder
    Finder -.->|5% fallback| Claude
    Finder -->|career_url| Extractor
    Claude -.->|career_url| Extractor
    Extractor -->|position_url| Results
    
    LinkedIn -.->|updates| Stats
    Finder -.->|updates| Stats
    Claude -.->|updates| Stats
    
    Results -->|contains| JSON
    Stats -->|contains| JSON
    JSON -->|1 file| User

    classDef input fill:#e1ffe1,stroke:#00aa00
    classDef data fill:#ffe1e1,stroke:#cc0000
    classDef process fill:#e1e1ff,stroke:#0000cc
    classDef output fill:#fff4e1,stroke:#cc8800
    
    class User,LinkedIn input
    class CompanyData,Results,Stats data
    class Finder,Claude,Extractor process
    class JSON output
```

---

## KEY MULTIPLICITY REFERENCE

### Critical Multiplicities Table

| Relationship | Source | Target | Multiplicity | Constraint |
|-------------|--------|--------|--------------|------------|
| **Input** | User | LinkedIn URL | 1 | Single URL per run |
| **Production** | LinkedInFetcher | CompanyData | 1..* | At least 1 company |
| **Processing** | Pipeline | CompanyData | 20..50 | FR-1.3 requirement |
| **Career Discovery** | CareerPageFinder | Tier1 | 1 | Always attempt |
| **Career Discovery** | CareerPageFinder | Tier2 | 0..1 | If Tier1 fails |
| **Career Discovery** | CareerPageFinder | Tier3 (Claude) | 0..1 | If Tier1&2 fail |
| **API Limit** | ClaudeFallback | API calls | 0..50 | Monthly maximum |
| **Result Creation** | Pipeline | JobSourceResult | 0..* | 0 if all fail |
| **Output** | OutputManager | JSON file | 1 | Single file per run |
| **Ownership** | Pipeline | All Components | 1 | Exactly one of each |

### Tier Success Distribution

```
Expected Distribution (per 100 companies):
├─ Tier 1 (Direct Paths):    80 companies (80%)
├─ Tier 2 (Homepage Scrape):  15 companies (15%)
└─ Tier 3 (Claude API):       5 companies (5%)
```

### Budget Allocation by Multiplicity

```
Monthly Budget: $50
├─ LinkedIn API:  $25 (unlimited companies within budget)
├─ Claude API:    $20 (max 50 calls × $0.40)
└─ Buffer:        $5
```

---

## Rendering Instructions

To view these diagrams:

1. **GitHub/GitLab:** Diagrams render automatically in README.md
2. **VSCode:** Install "Markdown Preview Mermaid Support" extension
3. **Online:** Copy to https://mermaid.live
4. **Command Line:** Use `mmdc` (mermaid-cli) to generate PNG/SVG

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i DESIGN_Step2_UML_Mermaid.md -o diagrams.png
```
