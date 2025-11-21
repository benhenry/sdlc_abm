# Historical Data Import

This directory contains sample CSV files for importing historical team data into SDLC SimLab.

## Quick Start

Import historical PR data and generate a calibrated scenario:

```bash
# Analyze historical data
python examples/import_historical_data.py data/samples/sample_prs.csv

# Generate scenario from data
python examples/import_historical_data.py data/samples/sample_prs.csv \
    --output data/scenarios/my_team.yaml \
    --name "My Team Q1 2024"

# Import and run simulation immediately
python examples/import_historical_data.py data/samples/sample_prs.csv --run
```

## CSV Format

### GitHub/GitLab Format

The importer expects a CSV file with the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `pr_id` (or `number`, `id`) | Yes | Unique PR identifier | 1001 |
| `title` | No | PR title | "Add user authentication" |
| `author` (or `user`, `creator`) | Yes | PR author username | alice |
| `created_at` | Yes | When PR was created | 2024-01-02T09:00:00Z |
| `merged_at` | No | When PR was merged | 2024-01-03T14:30:00Z |
| `closed_at` | No | When PR was closed | 2024-01-03T14:30:00Z |
| `reverted` | No | Was this PR reverted? | false |
| `reviewers` | No | Comma-separated reviewers | "bob,carol" |

### Supported Date Formats

- ISO 8601: `2024-01-15T10:30:00Z`
- Simple: `2024-01-15`
- US format: `01/15/2024`
- EU format: `15/01/2024`

## Exporting Data from GitHub

### Using GitHub API

```bash
# Get PRs for a repository (requires gh CLI)
gh pr list --repo owner/repo --limit 1000 --state all --json number,title,author,createdAt,mergedAt,closedAt > prs.json

# Convert JSON to CSV (Python)
python scripts/json_to_csv.py prs.json prs.csv
```

### Using GitHub GraphQL

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequests(first: 100, states: [MERGED, CLOSED]) {
      nodes {
        number
        title
        author { login }
        createdAt
        mergedAt
        closedAt
        reviews(first: 10) {
          nodes {
            author { login }
          }
        }
      }
    }
  }
}
```

## Exporting Data from GitLab

### Using GitLab API

```bash
# Get merge requests
curl "https://gitlab.com/api/v4/projects/{id}/merge_requests?state=all&per_page=100" \
  --header "PRIVATE-TOKEN: <token>" > mrs.json

# Convert to CSV format
```

## What Gets Analyzed?

The CSV importer analyzes your historical data and calculates:

### Team Metrics
- Total PRs created and merged
- Change failure rate (% of reverted PRs)
- Average cycle time (creation to merge)
- Throughput (PRs per week)
- Date range and duration

### Developer Metrics
For each developer:
- Total PRs created and merged
- Code quality (success rate)
- Productivity rate (PRs per week)
- Review capacity (reviews per week)
- Inferred experience level

## Generated Scenario

The importer creates a `ScenarioConfig` with:

1. **Developer configurations** based on analyzed metrics:
   - Name from historical data
   - Productivity rate from actual PRs/week
   - Code quality from success/revert ratio
   - Review capacity from actual reviews
   - Onboarding time set to 0 (already onboarded)

2. **Simulation parameters**:
   - Duration matching the historical period
   - Default communication loss factor (0.3)
   - Quadratic overhead model

3. **Metadata**:
   - Tags: `historical`, `imported`
   - Description with date range

## Example: Analyzing Your Team

```bash
# 1. Export your team's PR data (last 6 months)
gh pr list --repo my-org/my-repo \
  --limit 1000 \
  --state all \
  --json number,title,author,createdAt,mergedAt \
  > team_prs.json

# 2. Convert to CSV (you'll need to write a simple script)
python scripts/json_to_csv.py team_prs.json team_prs.csv

# 3. Import and analyze
python examples/import_historical_data.py team_prs.csv \
  --output data/scenarios/my_real_team.yaml \
  --name "My Team - Last 6 Months"

# 4. Run simulation with historical calibration
python examples/run_scenario.py data/scenarios/my_real_team.yaml

# 5. Compare simulation results with actual metrics
# The simulation should produce similar throughput and quality metrics
```

## Validation

After importing, compare simulation results with your actual metrics:

| Metric | Historical | Simulated | Difference |
|--------|-----------|-----------|------------|
| PRs/week | 10.0 | 11.25 | +12.5% |
| Change Failure Rate | 5.0% | 4.4% | -0.6% |
| Avg Cycle Time | 1.1 days | 3.2 days | +2.1 days |

**Note**: Some variance is expected due to the probabilistic nature of the simulation.

## Use Cases

### 1. Baseline Calibration
Import your team's data to create a realistic baseline scenario, then run "what-if" experiments:
- What if we add 3 junior developers?
- What if we improve code quality to 90%?
- What if we reduce meeting time?

### 2. Before/After Analysis
Import data from two time periods to see how your team evolved:
```bash
# Import Q1 data
python examples/import_historical_data.py q1_2024.csv \
  --output scenarios/team_q1.yaml --name "Team Q1"

# Import Q2 data
python examples/import_historical_data.py q2_2024.csv \
  --output scenarios/team_q2.yaml --name "Team Q2"

# Compare the two scenarios
```

### 3. New Team Projection
Use data from an existing team to model a new team:
```bash
# Import data from Team A
python examples/import_historical_data.py team_a.csv \
  --output scenarios/new_team_projection.yaml

# Edit the YAML to adjust team size/composition
# Run simulation to project outcomes
```

## Custom CSV Formats

If your CSV has different column names, use a custom mapping:

```python
from src.simulation.data_import import CSVDataImporter

importer = CSVDataImporter()
importer.import_generic_csv(
    'custom_export.csv',
    column_mapping={
        'pr_id': 'pull_request_number',
        'author': 'creator_name',
        'created_at': 'creation_date',
        'merged_at': 'merge_date',
    }
)

scenario = importer.generate_scenario("Custom Import")
scenario.to_yaml('data/scenarios/custom.yaml')
```

## Limitations

- **Minimum data**: Need at least 3 PRs per developer for meaningful analysis
- **Time range**: Best results with 4+ weeks of data
- **Missing reviewers**: If reviewer data is missing, review capacity may be underestimated
- **Reverts**: Manual tracking of reverts may be incomplete

## Tips for Best Results

1. **Include 6-12 weeks of data** for stable averages
2. **Mark reverted PRs** accurately in your export
3. **Include reviewer information** for better calibration
4. **Filter out bots** (Dependabot, etc.) from exports
5. **Normalize author names** if people have multiple accounts

## Troubleshooting

### "No PR records imported"
- Check CSV column names match expected format
- Verify date format is recognized
- Ensure `author` and `created_at` columns have data

### "Not enough developers with significant activity"
- Increase the time range of your export
- Lower the threshold (modify `total_prs >= 3` in code)
- Check that author names are consistent

### "Simulation results don't match historical data"
- Ensure onboarding_time is set to 0 for historical teams
- Check that productivity and quality metrics were calculated correctly
- Run multiple simulations and average results (probabilistic variation)

## Next Steps

After importing and validating your historical data:

1. **Baseline Scenario**: Save as `baseline.yaml`
2. **Experiment**: Create variations (add developers, change quality, etc.)
3. **Compare**: Use scenario comparison to see impacts
4. **Iterate**: Adjust and refine based on learnings

See `examples/README.md` for more scenario examples and usage patterns.
