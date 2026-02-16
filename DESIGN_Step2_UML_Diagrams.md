# Design Phase - Step 2: UML Class Diagrams
## AI Job Source Agent

**Version:** 1.0  
**Date:** 2025-02-13

---

## UML NOTATION LEGEND

```
Relationships:
──────────>    Association (uses)
──────────▷    Dependency (depends on)
◆──────────    Composition (owns, lifecycle bound)
◇──────────    Aggregation (has-a, independent lifecycle)
──────────▷    Inheritance (is-a)

Multiplicities:
1          Exactly one
0..1       Zero or one
*          Zero or many
1..*       One or many
n          Specific number

Visibility:
+          Public
-          Private
#          Protected
```

---

## DIAGRAM 1: COMPLETE CLASS DIAGRAM

```plantuml
@startuml AI_Job_Source_Agent_Complete

' ============ CONFIGURATION & UTILITIES ============
class Configuration {
    - apify_token: str
    - anthropic_api_key: str
    - career_paths: List[str]
    - career_keywords: List[str]
    - max_claude_calls: int
    - request_timeout: int
    - browser_timeout: int
    - output_dir: str
    __
    + load_from_env(): void
    + validate(): bool
    + get(key: str): Any
}

class Logger {
    - log_file: str
    - log_level: str
    - logs: List[Dict]
    __
    + info(message: str): void
    + error(message: str, exception: Exception): void
    + warning(message: str): void
    + save_logs(): void
}

class URLValidator {
    - timeout: int
    - user_agent: str
    __
    + is_valid(url: str): bool
    + normalize(url: str): str
    + make_absolute(base: str, relative: str): str
    - _check_status(url: str): int
}

' ============ DATA MODELS ============
class CompanyData {
    + company_name: str
    + company_url: str
    + linkedin_job_url: str
    + job_title: str
    __
    + to_dict(): Dict
    + validate_url(): bool
}

class JobSourceResult {
    + company_name: str
    + career_page_url: str
    + open_position_url: str
    + timestamp: datetime
    + source_tier: int
    + processing_time: float
    __
    + to_dict(): Dict
    + validate(): bool
    + __repr__(): str
}

class ExecutionStatistics {
    + total_processed: int
    + successful: int
    + failed: int
    + tier1_success: int
    + tier2_success: int
    + tier3_success: int
    + claude_api_calls: int
    + linkedin_api_calls: int
    + total_processing_time: float
    + start_time: datetime
    + end_time: datetime
    __
    + increment_success(tier: int): void
    + increment_failure(): void
    + calculate_success_rate(): float
    + calculate_heuristic_success_rate(): float
    + to_dict(): Dict
    + get_summary(): str
}

' ============ CORE COMPONENTS ============
class LinkedInFetcher {
    - api_token: str
    - base_url: str
    - max_items: int
    - request_timeout: int
    - api_calls_made: int
    - monthly_budget: float
    __
    + fetch_job_listings(linkedin_url: str, limit: int): List[Dict]
    + extract_company_data(raw_response: Dict): List[CompanyData]
    + handle_rate_limit(response: Dict): bool
    + validate_api_response(response: Dict): bool
    - _make_api_request(endpoint: str, params: Dict): Dict
    - _track_api_cost(items_fetched: int): void
}

class CareerPageFinder {
    - common_paths: List[str]
    - career_keywords: List[str]
    - request_timeout: int
    - max_retries: int
    - tier1_success_count: int
    - tier2_success_count: int
    - tier3_success_count: int
    __
    + find_career_page(company_url: str): Optional[str]
    + find_via_direct_paths(company_url: str): Optional[str]
    + scrape_homepage(company_url: str): Optional[str]
    + check_footer_nav(soup: BeautifulSoup): Optional[str]
    + make_absolute_url(base_url: str, relative_url: str): str
    + validate_url(url: str): bool
    - _matches_career_keyword(text: str, url: str): bool
    - _is_valid_career_page(url: str, content: str): bool
}

class ClaudeFallback {
    - api_key: str
    - model: str
    - max_tokens: int
    - calls_this_month: int
    - max_calls_per_month: int
    - monthly_budget: float
    __
    + find_career_page_ai(company_url: str): Optional[str]
    + check_monthly_limit(): bool
    + increment_call_counter(): void
    - _build_prompt(company_url: str): str
    - _parse_claude_response(response: Dict): Optional[str]
}

class PositionExtractor {
    - browser_timeout: int
    - page_load_timeout: int
    - job_selectors: List[str]
    - headless: bool
    - browser_context: BrowserContext
    __
    + extract_first_position(career_page_url: str): Optional[str]
    + navigate_to_page(url: str): Page
    + find_job_links(page: Page): List[str]
    + make_absolute_url(base_url: str, job_url: str): str
    - _initialize_browser(): Browser
    - _wait_for_content(page: Page): void
    - _extract_job_url(element: ElementHandle): str
}

class OutputManager {
    - output_dir: str
    - filename_template: str
    - results: List[JobSourceResult]
    - statistics: ExecutionStatistics
    __
    + add_result(result: JobSourceResult): void
    + save_to_json(filename: str): str
    + generate_filename(): str
    - _format_output(): Dict
    - _ensure_output_dir(): void
}

class JobSourcePipeline {
    - config: Configuration
    - linkedin_fetcher: LinkedInFetcher
    - career_finder: CareerPageFinder
    - claude_fallback: ClaudeFallback
    - position_extractor: PositionExtractor
    - output_manager: OutputManager
    - statistics: ExecutionStatistics
    - logger: Logger
    __
    + run(linkedin_url: str, max_companies: int): void
    + process_single_company(company: CompanyData): Optional[JobSourceResult]
    + handle_error(error: Exception, company: CompanyData): void
    - _initialize_components(): void
    - _validate_inputs(linkedin_url: str, max_companies: int): bool
    - _print_progress(current: int, total: int): void
}

' ============ RELATIONSHIPS ============

' Pipeline Composition (owns components)
JobSourcePipeline *-- "1" Configuration : owns
JobSourcePipeline *-- "1" LinkedInFetcher : owns
JobSourcePipeline *-- "1" CareerPageFinder : owns
JobSourcePipeline *-- "1" ClaudeFallback : owns
JobSourcePipeline *-- "1" PositionExtractor : owns
JobSourcePipeline *-- "1" OutputManager : owns
JobSourcePipeline *-- "1" ExecutionStatistics : owns
JobSourcePipeline *-- "1" Logger : owns

' OutputManager Composition
OutputManager *-- "0..*" JobSourceResult : contains
OutputManager *-- "1" ExecutionStatistics : contains

' Dependencies - Components use Configuration
LinkedInFetcher ..> Configuration : uses
CareerPageFinder ..> Configuration : uses
ClaudeFallback ..> Configuration : uses
PositionExtractor ..> Configuration : uses
OutputManager ..> Configuration : uses

' Dependencies - Components use Logger
LinkedInFetcher ..> Logger : logs to
CareerPageFinder ..> Logger : logs to
ClaudeFallback ..> Logger : logs to
PositionExtractor ..> Logger : logs to
OutputManager ..> Logger : logs to

' CareerPageFinder uses URLValidator
CareerPageFinder ..> URLValidator : uses
PositionExtractor ..> URLValidator : uses

' CareerPageFinder fallback to ClaudeFallback
CareerPageFinder --> "0..1" ClaudeFallback : fallback to

' Data flow associations
LinkedInFetcher --> "1..*" CompanyData : produces
JobSourcePipeline --> "1..*" CompanyData : processes
JobSourcePipeline --> "0..*" JobSourceResult : creates

' Statistics tracking
LinkedInFetcher --> ExecutionStatistics : updates
CareerPageFinder --> ExecutionStatistics : updates
ClaudeFallback --> ExecutionStatistics : updates

@enduml
```

---

## DIAGRAM 2: DETAILED RELATIONSHIP DIAGRAM

```plantuml
@startuml AI_Job_Source_Relationships

title Detailed Class Relationships & Multiplicities

' Simplified view focusing on relationships

package "Orchestration Layer" {
    class JobSourcePipeline {
        + run()
        + process_single_company()
    }
}

package "Data Acquisition Layer" {
    class LinkedInFetcher {
        + fetch_job_listings()
    }
}

package "Career Discovery Layer" {
    class CareerPageFinder {
        + find_career_page()
    }
    
    class ClaudeFallback {
        + find_career_page_ai()
    }
    
    class URLValidator {
        + is_valid()
    }
}

package "Position Extraction Layer" {
    class PositionExtractor {
        + extract_first_position()
    }
}

package "Output Layer" {
    class OutputManager {
        + save_to_json()
    }
}

package "Data Models" {
    class CompanyData {
        + company_name
        + company_url
    }
    
    class JobSourceResult {
        + company_name
        + career_page_url
        + open_position_url
    }
    
    class ExecutionStatistics {
        + total_processed
        + successful
        + failed
    }
}

package "Infrastructure" {
    class Configuration {
        + apify_token
        + career_paths
    }
    
    class Logger {
        + info()
        + error()
    }
}

' ============ KEY RELATIONSHIPS WITH MULTIPLICITIES ============

' COMPOSITION (black diamond) - Strong ownership
JobSourcePipeline *-- "1" LinkedInFetcher : owns >
JobSourcePipeline *-- "1" CareerPageFinder : owns >
JobSourcePipeline *-- "1" ClaudeFallback : owns >
JobSourcePipeline *-- "1" PositionExtractor : owns >
JobSourcePipeline *-- "1" OutputManager : owns >
JobSourcePipeline *-- "1" Configuration : owns >
JobSourcePipeline *-- "1" Logger : owns >
JobSourcePipeline *-- "1" ExecutionStatistics : owns >

OutputManager *-- "0..*" JobSourceResult : contains >
OutputManager *-- "1" ExecutionStatistics : contains >

' ASSOCIATION (line) - Uses relationship
LinkedInFetcher --> "1..*" CompanyData : << produces >>
note on link
    LinkedIn API returns
    1 or more companies
end note

JobSourcePipeline --> "20..50" CompanyData : << processes >>
note on link
    FR-1.3: Process 
    20-50 companies/run
end note

JobSourcePipeline --> "0..*" JobSourceResult : << creates >>
note on link
    0 if all fail,
    up to 50 if all succeed
end note

' DEPENDENCY (dashed arrow) - Temporary usage
CareerPageFinder ..> "0..1" ClaudeFallback : << fallback >>
note on link
    Only used when
    Tier 1 & 2 fail
    (5% of cases)
end note

CareerPageFinder ..> "1" URLValidator : << validates >>
PositionExtractor ..> "1" URLValidator : << validates >>

' All components depend on Configuration
LinkedInFetcher ..> Configuration : << reads config >>
CareerPageFinder ..> Configuration : << reads config >>
ClaudeFallback ..> Configuration : << reads config >>
PositionExtractor ..> Configuration : << reads config >>

' All components depend on Logger
LinkedInFetcher ..> Logger : << logs events >>
CareerPageFinder ..> Logger : << logs events >>
ClaudeFallback ..> Logger : << logs events >>
PositionExtractor ..> Logger : << logs events >>
OutputManager ..> Logger : << logs events >>

' Statistics updates
LinkedInFetcher --> "1" ExecutionStatistics : << updates >>
CareerPageFinder --> "1" ExecutionStatistics : << updates >>
ClaudeFallback --> "1" ExecutionStatistics : << updates >>

@enduml
```

---

## DIAGRAM 3: INTERACTION SEQUENCE DIAGRAM

```plantuml
@startuml Pipeline_Sequence_Diagram

title Main Pipeline Execution Flow

actor User
participant "JobSourcePipeline" as Pipeline
participant "LinkedInFetcher" as LinkedIn
participant "CareerPageFinder" as CareerFinder
participant "ClaudeFallback" as Claude
participant "PositionExtractor" as Extractor
participant "OutputManager" as Output
participant "ExecutionStatistics" as Stats
participant "Logger" as Log

User -> Pipeline: run(linkedin_url, max_companies=50)
activate Pipeline

Pipeline -> Log: info("Starting pipeline")
Pipeline -> Stats: start_time = now()

' LinkedIn Data Acquisition
Pipeline -> LinkedIn: fetch_job_listings(url, limit=50)
activate LinkedIn
LinkedIn -> LinkedIn: _make_api_request()
LinkedIn -> Stats: linkedin_api_calls++
LinkedIn --> Pipeline: List[CompanyData] (1..50)
deactivate LinkedIn

' Loop through companies
loop for each CompanyData [1..50]
    
    Pipeline -> Pipeline: process_single_company(company)
    activate Pipeline
    
    ' Career Page Discovery - Tier 1 & 2
    Pipeline -> CareerFinder: find_career_page(company_url)
    activate CareerFinder
    
    CareerFinder -> CareerFinder: find_via_direct_paths()
    alt Path found (80% of cases)
        CareerFinder -> Stats: tier1_success++
        CareerFinder --> Pipeline: career_url
    else Path not found
        CareerFinder -> CareerFinder: scrape_homepage()
        alt Homepage scraped (15% of cases)
            CareerFinder -> Stats: tier2_success++
            CareerFinder --> Pipeline: career_url
        else Homepage failed (5% of cases)
            ' Career Page Discovery - Tier 3
            CareerFinder -> Claude: find_career_page_ai(company_url)
            activate Claude
            
            alt Monthly limit not reached
                Claude -> Claude: check_monthly_limit()
                Claude -> Claude: _build_prompt()
                Claude -> Claude: API call to Anthropic
                Claude -> Stats: tier3_success++
                Claude -> Stats: claude_api_calls++
                Claude --> CareerFinder: career_url
            else Monthly limit reached
                Claude -> Log: warning("API limit reached")
                Claude --> CareerFinder: None
            end
            deactivate Claude
            
            CareerFinder --> Pipeline: career_url or None
        end
    end
    deactivate CareerFinder
    
    alt career_url found
        ' Position Extraction
        Pipeline -> Extractor: extract_first_position(career_url)
        activate Extractor
        Extractor -> Extractor: navigate_to_page()
        Extractor -> Extractor: find_job_links()
        Extractor --> Pipeline: position_url or None
        deactivate Extractor
        
        alt position_url found
            ' Create result
            Pipeline -> Pipeline: create JobSourceResult
            Pipeline -> Output: add_result(result)
            activate Output
            Output -> Stats: successful++
            deactivate Output
            Pipeline -> Log: info("Success: {company_name}")
        else position_url not found
            Pipeline -> Stats: failed++
            Pipeline -> Log: warning("No positions found")
        end
    else career_url not found
        Pipeline -> Stats: failed++
        Pipeline -> Log: error("Career page not found")
    end
    
    deactivate Pipeline
end

' Save results
Pipeline -> Stats: end_time = now()
Pipeline -> Output: save_to_json()
activate Output
Output -> Output: generate_filename()
Output -> Output: _format_output()
Output -> Log: info("Saved to {filename}")
Output --> Pipeline: filename
deactivate Output

Pipeline -> Log: info("Pipeline completed")
Pipeline -> Stats: get_summary()
Pipeline --> User: Execution complete

deactivate Pipeline

@enduml
```

---

## DIAGRAM 4: CAREER FINDER STATE MACHINE

```plantuml
@startuml Career_Finder_State_Machine

title Career Page Discovery - 3-Tier Strategy

[*] --> Tier1_DirectPaths

state Tier1_DirectPaths {
    [*] --> Testing
    Testing --> Success : Path found (80%)
    Testing --> Failed : All paths exhausted
}

Tier1_DirectPaths --> [*] : career_url returned
Tier1_DirectPaths --> Tier2_HomepageScraping : Failed

state Tier2_HomepageScraping {
    [*] --> Scraping
    Scraping --> ExtractingLinks
    ExtractingLinks --> MatchingKeywords
    MatchingKeywords --> Success : Match found (15%)
    MatchingKeywords --> Failed : No matches
}

Tier2_HomepageScraping --> [*] : career_url returned
Tier2_HomepageScraping --> Tier3_ClaudeAPI : Failed

state Tier3_ClaudeAPI {
    [*] --> CheckingLimit
    CheckingLimit --> CallingAPI : limit OK
    CheckingLimit --> Failed : limit exceeded
    CallingAPI --> ParsingResponse
    ParsingResponse --> Success : URL extracted (5%)
    ParsingResponse --> Failed : Invalid response
}

Tier3_ClaudeAPI --> [*] : career_url or None

Success --> [*]
Failed --> [*]

note right of Tier1_DirectPaths
    FREE
    Common paths:
    /careers, /jobs, etc.
end note

note right of Tier2_HomepageScraping
    FREE
    BeautifulSoup
    keyword matching
end note

note right of Tier3_ClaudeAPI
    PAID ($$$)
    Max 50 calls/month
    $0.30-0.40/call
end note

@enduml
```

---

## DIAGRAM 5: COMPONENT DIAGRAM

```plantuml
@startuml Component_Diagram

title System Component Architecture

package "Job Source Agent System" {
    
    [Pipeline Orchestrator] as Pipeline
    
    package "Data Acquisition" {
        [LinkedIn Fetcher] as LinkedIn
        interface "Apify API" as ApifyAPI
        LinkedIn --> ApifyAPI
    }
    
    package "Career Discovery" {
        [Career Page Finder] as Finder
        [Claude Fallback] as Claude
        [URL Validator] as Validator
        interface "Anthropic API" as ClaudeAPI
        
        Finder --> Validator
        Finder ..> Claude : fallback
        Claude --> ClaudeAPI
    }
    
    package "Position Extraction" {
        [Position Extractor] as Extractor
        interface "Playwright Browser" as Browser
        Extractor --> Browser
    }
    
    package "Output Management" {
        [Output Manager] as Output
        database "JSON Files" as JSON
        Output --> JSON
    }
    
    package "Infrastructure" {
        [Configuration Manager] as Config
        [Logger] as Log
        [Execution Statistics] as Stats
    }
    
    ' Dependencies
    Pipeline --> LinkedIn
    Pipeline --> Finder
    Pipeline --> Claude
    Pipeline --> Extractor
    Pipeline --> Output
    Pipeline --> Config
    Pipeline --> Log
    Pipeline --> Stats
    
    LinkedIn ..> Config
    LinkedIn ..> Log
    Finder ..> Config
    Finder ..> Log
    Claude ..> Config
    Claude ..> Log
    Extractor ..> Config
    Extractor ..> Log
    Output ..> Config
    Output ..> Log
    
    LinkedIn --> Stats
    Finder --> Stats
    Claude --> Stats
}

note top of Pipeline
    Main entry point
    Coordinates all components
end note

note right of LinkedIn
    Multiplicity: 1..*
    Produces 20-50 companies
    Budget: $20-25/month
end note

note right of Claude
    Multiplicity: 0..1
    Used only 5% of time
    Budget: $15-20/month
    Limit: 50 calls/month
end note

note bottom of Output
    Multiplicity: 0..*
    Contains 0-50 results
    Format: job_sources_YYYY-MM-DD.json
end note

@enduml
```

---

## KEY RELATIONSHIP SUMMARY

### 1. COMPOSITION (◆──) - Strong Ownership

| Owner | Owns | Multiplicity | Lifecycle |
|-------|------|--------------|-----------|
| JobSourcePipeline | LinkedInFetcher | 1 | Bound |
| JobSourcePipeline | CareerPageFinder | 1 | Bound |
| JobSourcePipeline | ClaudeFallback | 1 | Bound |
| JobSourcePipeline | PositionExtractor | 1 | Bound |
| JobSourcePipeline | OutputManager | 1 | Bound |
| JobSourcePipeline | Configuration | 1 | Bound |
| JobSourcePipeline | Logger | 1 | Bound |
| JobSourcePipeline | ExecutionStatistics | 1 | Bound |
| OutputManager | JobSourceResult | 0..* | Bound |
| OutputManager | ExecutionStatistics | 1 | Bound |

**Meaning:** Pipeline creates and destroys these components. They cannot exist independently.

---

### 2. ASSOCIATION (──) - Uses Relationship

| Client | Uses | Multiplicity | Direction | Notes |
|--------|------|--------------|-----------|-------|
| LinkedInFetcher | CompanyData | 1..* | produces | Returns 1+ companies |
| JobSourcePipeline | CompanyData | 20..50 | processes | FR-1.3 requirement |
| JobSourcePipeline | JobSourceResult | 0..* | creates | 0 if all fail, max 50 |
| CareerPageFinder | ExecutionStatistics | 1 | updates | Tier success counters |
| ClaudeFallback | ExecutionStatistics | 1 | updates | API call tracking |

**Meaning:** These are primary data flows through the system.

---

### 3. DEPENDENCY (- - ->) - Temporary Usage

| Client | Depends On | Multiplicity | Condition | Frequency |
|--------|-----------|--------------|-----------|-----------|
| CareerPageFinder | ClaudeFallback | 0..1 | When Tier 1&2 fail | 5% of time |
| CareerPageFinder | URLValidator | 1 | Always | Every validation |
| PositionExtractor | URLValidator | 1 | Always | Every validation |
| All Components | Configuration | 1 | Initialization | Once at startup |
| All Components | Logger | 1 | On events | Throughout execution |

**Meaning:** Temporary, conditional, or utility relationships.

---

### 4. CRITICAL MULTIPLICITIES

#### Input Multiplicity (FR-1.3):
```
User Input → Pipeline: 1 (single LinkedIn URL)
Pipeline → Companies: 20..50 (process this many)
```

#### Processing Multiplicity:
```
LinkedIn API → CompanyData: 1..* (at least one)
CareerPageFinder → career_url: 0..1 (found or not)
PositionExtractor → position_url: 0..1 (found or not)
Pipeline → JobSourceResult: 0..* (0 to max_companies)
```

#### Tier Strategy Multiplicity:
```
CareerPageFinder → Tier1: 1 (always try)
CareerPageFinder → Tier2: 0..1 (if Tier1 fails)
CareerPageFinder → Tier3: 0..1 (if Tier1&2 fail, max 50/month)
```

#### Output Multiplicity:
```
OutputManager → JobSourceResult: 0..* (collected results)
OutputManager → JSON file: 1 (single output file)
```

---

## DESIGN PATTERNS IN RELATIONSHIPS

### 1. Strategy Pattern
```
CareerPageFinder
    ↓ uses
[Tier1Strategy] [Tier2Strategy] [Tier3Strategy(ClaudeFallback)]
```
**Relationship:** Dependency with conditional selection

### 2. Facade Pattern
```
User → JobSourcePipeline → [All Subsystems]
```
**Relationship:** JobSourcePipeline owns and orchestrates all components

### 3. Singleton Pattern
```
All Components → Configuration (shared instance)
All Components → Logger (shared instance)
```
**Relationship:** Dependency on shared resources

---

## RELATIONSHIP CONSTRAINTS

### Temporal Constraints:
1. **Configuration** must be initialized before any component
2. **Logger** must be available before any logging occurs
3. **LinkedInFetcher** executes before **CareerPageFinder**
4. **CareerPageFinder** executes before **PositionExtractor**
5. **OutputManager** executes after all processing complete

### Cardinality Constraints:
1. **JobSourcePipeline** has exactly 1 of each component
2. **CompanyData** produced: minimum 1, maximum 50
3. **JobSourceResult** produced: minimum 0, maximum 50
4. **ClaudeFallback** calls: maximum 50 per month
5. **OutputManager** creates exactly 1 JSON file per run

### Dependency Constraints:
1. **CareerPageFinder** depends on **URLValidator** (mandatory)
2. **CareerPageFinder** depends on **ClaudeFallback** (optional)
3. All components depend on **Configuration** (mandatory)
4. All components depend on **Logger** (optional but recommended)

---

**DIAGRAMS GENERATED:**
1. ✓ Complete Class Diagram (all 12 classes)
2. ✓ Detailed Relationship Diagram (with multiplicities)
3. ✓ Sequence Diagram (main execution flow)
4. ✓ State Machine (Career Finder tiers)
5. ✓ Component Diagram (system architecture)

**NEXT STEP:** Review diagrams and proceed to implementation phase or refine design.
