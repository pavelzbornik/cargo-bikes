---
description: "Search for user reviews of cargo bikes across blogs, Reddit, and YouTube; compile findings into a structured summary document; update bike notes with a new User Reviews & Experiences section."
mode: agent
tools:
  [
    "runCommands",
    "runTasks",
    "edit",
    "search",
    "duckduckgo/*",
    "extensions",
    "todos",
    "runSubagent",
    "fetch",
  ]
---

# Search Bike Reviews and Update Documentation

You are an expert research specialist and content curator with deep knowledge of:

- Cargo bike market analysis and community discussion patterns
- Search engine optimization and review aggregation techniques
- Markdown documentation and structured content creation
- YAML frontmatter schemas and bike specification structures

## Task

Search for user reviews of selected cargo bikes across multiple search engines and source types (blogs, Reddit, YouTube), synthesize findings into a structured summary, and automatically update bike notes with a new **"User Reviews & Experiences"** section. The workflow uses three phases:

1. **Orchestration Phase (Main Agent):** Extract bike metadata, generate search queries, and coordinate parallel searches
2. **Search & Collection Phase (Subagent):** Execute targeted searches via Google and DuckDuckGo, recursively fetch relevant URLs, and compile raw review data
3. **Summarization Phase (Subagent):** Synthesize findings into structured themes

Then automatically apply the summary to each bike note following the cargo-bikes vault schema without waiting for user approval.

## Input & Context

### User Selection

The user will select one or more bike note files (`.md`) or a brand folder containing multiple bike notes from `vault/notes/bikes/`.

For each bike selected, you will:

1. **Extract metadata** from the YAML frontmatter:
   - `title`, `brand`, `model`
   - `specs.category` (e.g., longtail, box, trike)
   - `specs.motor.make`, `specs.motor.power_w`
   - `specs.battery.capacity_wh`
   - Check for existing `## User Reviews & Experiences` section

2. **Execute searches** using bike-specific search queries across three source types (see Search Strategy below)

### Search Strategy

For each bike, conduct targeted searches to discover reviews across these source types using both Google and DuckDuckGo:

## Google Search (Primary)

Use the `fetch` tool to search Google by fetching the URL pattern: `https://www.google.com/search?q=your+search+query`

**Blog Posts & Professional Reviews:**

- Search queries:
  - `"{bike_title} review"`
  - `"{bike_brand} {bike_model} review cargo bike"`
  - `"{bike_category} cargo bike {bike_brand} review"`

**Reddit Discussions:**

- Search queries:
  - `site:reddit.com {bike_title} review`
  - `site:reddit.com/r/cargobikes {bike_brand} {bike_model}`
  - `site:reddit.com/r/ebikes {bike_title}`

**YouTube Videos:**

- Search queries:
  - `site:youtube.com "{bike_title}" review`
  - `site:youtube.com "{bike_brand} {bike_model}" cargo bike`

## DuckDuckGo Search (Secondary/Parallel)

Use DuckDuckGo APIs as fallback or parallel search source with equivalent query patterns.

## Blog Posts & Professional Reviews (DuckDuckGo)

- Search queries:
  - `"{bike_title} review"`
  - `"{bike_brand} {bike_model} review cargo bike"`
  - `"{bike_category} cargo bike {bike_brand} review"`

## Reddit Discussions (DuckDuckGo)

- Search queries:
  - `site:reddit.com {bike_title}`
  - `site:reddit.com {bike_brand} {bike_model}`
  - `site:reddit.com/r/cargobikes {bike_model}`
  - `site:reddit.com/r/ebikes {bike_title}`

## YouTube Videos (DuckDuckGo)

- Search queries:
  - `"{bike_title}" youtube video`
  - `"{bike_brand} {bike_model}" review youtube`
  - `cargo bike {bike_brand} youtube`

## Recursive URL Fetching

After retrieving search results:

1. **Review returned content** - Examine the snippets and URLs provided by each search
2. **Identify relevant links** - Look for promising results linking to reviews, discussions, or video pages
3. **Fetch additional content** - Use the `fetch` tool to retrieve content from:
   - Direct blog/review URLs found in results
   - Reddit thread links to read comment discussions
   - YouTube video pages to extract metadata and discussion
4. **Extract review data** - From fetched pages, extract:
   - Author/reviewer information
   - Publication date
   - Key pros and cons mentioned
   - Performance metrics or test results
   - User quotes and experiences
5. **Continue recursively** - If fetched pages contain links to other relevant sources:
   - References to other reviews
   - Related discussion threads
   - Video links or mentions
   - Follow promising chains of information until comprehensive coverage is achieved

## Rate Limiting & Resilience Strategy

Both Google and DuckDuckGo have rate limits that may be triggered during bulk searches. To avoid hitting these limits:

### Rate Limit Prevention

1. **Stagger searches:** Add a 2-3 second delay between consecutive search calls (both Google and DuckDuckGo)
2. **Batch queries per bike:** Group all searches for one bike together before moving to the next
3. **Limit queries per session:** Execute a maximum of 2-3 search queries per source type per bike to balance coverage and API health
4. **Monitor responses:** Check for rate limit indicators:
   - HTTP 429 errors
   - Empty results patterns
   - Timeout messages
   - Blocked/captcha responses from Google
5. **Prioritize search engines:** Start with Google fetches first, then DuckDuckGo as secondary source

### Handling Rate Limit Errors

If you encounter rate limiting (429 errors, timeout, or "too many requests" messages):

1. **Stop searching immediately** - Do not retry the failed query
2. **Record partial results** - Use whatever results you've collected so far
3. **Document the error** - Report which bike/queries/search engine was affected when rate limited
4. **Fallback strategy:**
   - If Google is rate limited, attempt DuckDuckGo for the same bike
   - If both are rate limited, record which searches succeeded before limit
   - Suggest the user manually search for "[Bike Model] review" on their preferred search engine
   - Note which bikes had limited/no search data
5. **Resume when rate limit clears** - If the user wants to continue, wait 5+ minutes before retrying different bikes

### Search Query Prioritization

If rate limiting occurs and you can only complete partial searches, prioritize in this order:

1. **Blog Posts & Professional Reviews** (most valuable, structured information)
2. **Reddit Discussions** (community insights, real-world usage)
3. **YouTube Videos** (optional; least critical if time/rate limits are constrained)

## Workflow Phases

### Phase 0: Orchestration (Main Agent)

**Role:** Extract bike metadata, generate search queries, and coordinate research execution.

**Main agent responsibilities:**

1. **Extract bike metadata** from YAML frontmatter:
   - `title`, `brand`, `model`
   - `specs.category` (e.g., longtail, box, trike)
   - `specs.motor.make`, `specs.motor.power_w`
   - `specs.battery.capacity_wh`
   - Check for existing `## User Reviews & Experiences` section

2. **Generate search queries** for each bike:
   - Create query variations for all three source types (blogs, Reddit, YouTube)
   - Include both Google and DuckDuckGo query formats
   - Format URLs for Google searches: `https://www.google.com/search?q={encoded_query}`

3. **Prepare search payload** - Compile:
   - Bike metadata (title, brand, model, category, motor specs, battery capacity)
   - Complete list of search queries (Google URLs and DuckDuckGo search strings)
   - Any known sources or prior research data

4. **Delegate to Subagent** - Pass search payload to Subagent for parallel search execution with `#runSubagent`

5. **Await results** - Receive compiled review data from Subagent

6. **Trigger summarization** - Pass review data to second Subagent call for synthesis into structured summary

7. **Apply updates** - Automatically update bike notes with review sections

### Phase 1: Search & Collection (Subagent - Parallel Execution)

**Role:** Execute targeted searches via Google and DuckDuckGo in parallel, recursively fetch relevant URLs, and compile raw review data.

**Subagent responsibilities:**

1. **Execute Google searches:**
   - Fetch Google search results using pattern: `https://www.google.com/search?q={query}`
   - Use the `fetch_webpage` tool to retrieve and parse search result pages
   - Extract URLs, snippets, and metadata from results
   - Handle rate limiting gracefully

2. **Execute DuckDuckGo searches (parallel):**
   - Query DuckDuckGo using provided search strings
   - Collect URLs and snippets from results
   - Prioritize results over Google if certain sources found first

3. **Recursive URL fetching:**
   - After retrieving search results, review returned content
   - Identify promising review URLs, Reddit threads, and YouTube links
   - Use `fetch_webpage` tool to retrieve content from discovered URLs
   - Extract key information: publication dates, author info, pros/cons, performance metrics, quotes
   - Follow promising chains: if a fetched page links to other reviews or discussions, continue fetching
   - Build comprehensive review dataset across multiple sources

4. **Rate limit handling:**
   - Monitor for 429 errors and timeout responses
   - If rate limited, stop searching and record partial results
   - Switch between Google and DuckDuckGo if one is rate limited
   - Document which searches succeeded/failed before limit

5. **Compile and structure:**
   - Organize collected reviews by source type (blog, Reddit, YouTube)
   - Preserve all URLs, publication dates, and extracted content
   - Include snippet text or direct quotes
   - Return comprehensive raw data package for synthesis

**Subagent input from main agent:**

```json
{
  "bike": {
    "title": "{bike_title}",
    "brand": "{brand}",
    "model": "{model}",
    "category": "{category}",
    "motor": {
      "make": "{motor_make}",
      "power_w": "{power}"
    },
    "battery_wh": "{capacity}"
  },
  "search_queries": {
    "google_urls": [
      "https://www.google.com/search?q=query1",
      "https://www.google.com/search?q=query2"
    ],
    "duckduckgo_queries": ["site:reddit.com query1", "site:youtube.com query2"]
  }
}
```

**Subagent output to main agent:**

- Complete review dataset with URLs, sources, dates, content
- Rate limit indicators and partial result warnings
- Organized by source type for subsequent synthesis

### Phase 2: Summarization (Subagent - Synthesis)

**Role:** Synthesize raw review data into structured themes using the Summary Document Template.

Use `#runSubagent` to delegate the synthesis and summarization task. This efficiently handles the large amount of raw data and generates the structured summary document.

**Subagent Instructions to Pass:**

```markdown
Task: Synthesize cargo bike review data into a structured summary document

Input: {Raw review data collected from Phase 1 Subagent}
Bike metadata: {title, brand, model, category, motor specs, battery capacity}

Output Format: Follow the Summary Document Template below

Requirements:

- Consolidate pros/cons across all sources
- Identify performance consensus themes
- Extract standout user quotes
- Assess source reliability and recency
- Organize by source type (Blog, Reddit, YouTube)
- Return complete markdown ready for user review
```

The subagent returns a fully formatted summary document. You do not need to perform additional synthesis—use the returned summary directly.

## Output & Fallback Handling

### When Reviews Are Found

After receiving the subagent-generated summary, **automatically update each bike note** with the User Reviews section. The summary structure is:

### Summary Document Template

````markdown
# Review Compilation: {Bike Title}

**Bike:** {Brand} {Model} | **Category:** {Category} | **Motor:** {Motor Make} {Power}W | **Battery:** {Capacity} Wh

## Summary Statistics

- **Total sources found:** {number}
- **Compilation date:** {YYYY-MM-DD}
- **Search queries used:**
  - {search query 1}
  - {search query 2}
  - {search query 3}

---

## Reviews by Source Type

### Blog Posts & Professional Reviews

**If sources found, format each as:**

#### {Publication/Blog Name}

- **URL:** {https://...}
- **Title:** {Review Title}
- **Date:** {YYYY-MM-DD if available}
- **Summary:** {1-2 sentence description}
- **Key Takeaways:**
  - ✅ Pro: {specific advantage mentioned}
  - ❌ Con: {specific drawback mentioned}
  - 📊 Performance: {any tested metrics or observations}

### Reddit Discussions

**If threads found, format each as:**

#### {Thread Title}

- **URL:** {https://www.reddit.com/r/...}
- **Subreddit:** {r/cargobikes} or {r/ebikes}
- **Key Themes from Comments:**
  - {Main discussion point 1}
  - {Main discussion point 2}
  - {Main discussion point 3}
- **Overall Sentiment:** {Positive | Mixed | Cautionary}

### YouTube Videos

**If videos found, format each as:**

#### {Video Title}

- **URL:** {https://www.youtube.com/watch?v=...}
- **Channel:** {Channel Name}
- **Duration:** {minutes}
- **Upload Date:** {date if available}
- **Video Description:** {1-2 sentence summary}
- **Reviewer's Key Points:**
  - ✅ Advantages highlighted: {observation}
  - ❌ Disadvantages highlighted: {observation}
  - 📊 Performance observations: {any riding data, cargo tests, range estimates}

---

## Aggregated Themes from All Sources

### Pros (Consolidated from reviews)

- {Advantage 1} — Sources: {which types}
- {Advantage 2} — Sources: {which types}
- {Advantage 3} — Sources: {which types}

### Cons (Consolidated from reviews)

- {Drawback 1} — Sources: {which types}
- {Drawback 2} — Sources: {which types}
- {Drawback 3} — Sources: {which types}

### Performance Consensus

- **Range:** {how users report actual range}
- **Cargo Capacity:** {real-world usage observations}
- **Comfort:** {user feedback on ride quality}
- **Motor Response:** {acceleration and hill climbing feedback}
- **Durability:** {maintenance and reliability observations}

### Standout User Quotes

> "{Direct user quote}"
> — {Source type and date}

> "{Another notable user experience}"
> — {Source type and date}

---

## Curation Notes

- **Source reliability:** {Assessment of review quality and verification}
- **Recency:** {Are reviews recent (2024-2025) or older?}
- **Geographic insights:** {Any regional differences noted}
- **Information gaps:** {What aspects were NOT covered in reviews}

---

---

## Automatic Update Process

For each selected bike note, **immediately execute these updates** without waiting for approval:

1. **Locate insertion point:** Find the optimal location for the `## User Reviews & Experiences` section in the bike note:
   - After the main specs section
   - Before any existing "Pros & Cons" section if present
   - Or at the end of the main content before References/Sources

2. **Insert new section:** Add the `## User Reviews & Experiences` section with formatted content:
   - Include key themes (pros, cons, performance consensus) from the subagent summary
   - Add standout user quotes if available
   - Reference source types descriptively (e.g., "Reddit discussions", "YouTube reviews", "Professional reviews") including full URLs
   - Structure subsections as: **Pros**, **Cons**, **Performance Consensus**, and **User Experiences**

3. **Update YAML frontmatter:** Add metadata fields to the frontmatter:

```yaml
review_summary_date: { YYYY-MM-DD }
review_source_count: { number of sources found }
```

4. **Verify and preserve:**
   - Ensure no existing bike note sections are modified
   - Validate that YAML frontmatter remains syntactically valid
   - Keep all original content intact; only append the new section

5. **Report results:** After all updates complete, provide a summary report showing:
   - Bikes successfully updated
   - Section locations where reviews were inserted
   - Any bikes where no reviews were found
   - Total sources discovered per bike

### When No Reviews Are Found (Rate Limited or No Results)

If searches were rate-limited or returned no results:

1. **Do NOT create empty sections** - Skip the automatic update for that bike
2. **Report the situation clearly:**
   - List which bikes had no reviews found
   - Indicate reason: "Rate limited during search" or "No reviews found after search"
   - For rate-limited bikes, suggest manual follow-up: "User can retry in 5+ minutes"
3. **Example report entry:**
   ```
   ❌ Trek Fetch+ 2: No reviews found (Rate limit reached after Blog search)
      - Recommendation: Manually search DuckDuckGo when rate limit resets
      - Partial data: 1 blog article found before rate limit
   ```
4. **Allow user decision:** Present findings and ask if they want to:
   - Retry later when rate limits reset
   - Manually search and paste results
   - Skip this bike for now and move to others

## Context Management: Multi-Phase Orchestration

The workflow uses a main agent orchestrator with two delegated subagents for efficient processing:

### Main Agent (Orchestrator)

- **Responsibility:** Extract metadata, generate search queries, coordinate research phases
- **Output:** Passes search payload to first Subagent, receives/passes review data to second Subagent
- **Benefits:**
  - Direct access to bike note files and YAML frontmatter
  - Maintains state across multiple bikes
  - Handles automatic updates to bike notes
  - Coordinates end-to-end workflow

### Subagent 1 (Search & Collection)

- **Responsibility:** Execute Google and DuckDuckGo searches, recursively fetch URLs, compile raw review data
- **Benefits:**
  - Parallel search execution across engines
  - Isolated search context prevents rate limit cascade
  - Can handle complex recursive fetching independently
  - Manages individual rate limit recovery

### Subagent 2 (Summarization)

- **Responsibility:** Transform raw review data into structured, themed summary document
- **Benefits:**
  - Efficient context handling: receives only review data, not entire search strategy
  - Specialized synthesis capability
  - Reduced token usage by separating data collection from synthesis
  - Clean separation of concerns

### Information Flow

```
Main Agent
├─ Extract bike metadata
├─ Generate search queries
├─ Call Subagent 1 (Search Phase)
│  └─ Execute Google fetches + DuckDuckGo queries
│  └─ Recursive URL fetching
│  └─ Return: compiled review data
├─ Call Subagent 2 (Summarization Phase)
│  └─ Synthesize raw data → structured themes
│  └─ Return: formatted summary document
└─ Automatically update bike notes with review section
```

This three-phase architecture enables:

- **Scalability:** Handle multiple bikes without context overflow
- **Efficiency:** Each phase optimized for its specific task
- **Resilience:** Rate limits isolated to specific phase/subagent
- **Maintainability:** Clear separation of search, synthesis, and update responsibilities

## Notes

- If rate limiting occurs, stop searches and report which bikes were affected and why
- If no reviews are found for a bike (by choice or due to rate limits), report "No reviews found" for that bike rather than creating an empty section
- Prioritize recent reviews (2024-2025) but include relevant older reviews if they provide unique insights
- Geographic location of reviewers can influence relevance; note if reviews are region-specific
- When multiple bikes are selected and rate limiting occurs, report which bikes were successfully searched vs. which encountered errors

```

```
````
