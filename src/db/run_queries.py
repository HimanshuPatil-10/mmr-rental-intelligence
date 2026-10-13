"""
SQL query runner for MMR Rental Market Intelligence.

This module:
- Loads enriched data into SQLite database
- Executes all analytical queries
- Exports results to CSV files
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging
from glob import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENRICHED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"
DB_PATH = PROJECT_ROOT / "data" / "processed" / "mmr_rentals.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"
QUERIES_DIR = PROJECT_ROOT / "sql" / "queries"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "sql_outputs"


def create_database():
    """Create SQLite database and load data."""
    logger.info("Creating SQLite database...")

    # Load enriched data
    logger.info(f"Loading data from {ENRICHED_DATA_PATH}")
    df = pd.read_csv(ENRICHED_DATA_PATH)
    logger.info(f"Loaded {len(df)} rows")

    # Create database connection
    conn = sqlite3.connect(DB_PATH)

    # Load data into database
    logger.info("Loading data into database...")
    df.to_sql('rentals', conn, if_exists='replace', index=False)

    logger.info(f"Database created at {DB_PATH}")
    return conn


def execute_query(conn, query_path: Path, output_path: Path):
    """Execute a single SQL query and save results to CSV."""
    logger.info(f"Executing query: {query_path.name}")

    # Read query
    with open(query_path, 'r', encoding='utf-8') as f:
        query = f.read()

    # Execute query
    try:
        result_df = pd.read_sql_query(query, conn)
        logger.info(f"Query returned {len(result_df)} rows")

        # Save to CSV
        result_df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")

        return result_df
    except Exception as e:
        logger.error(f"Error executing query {query_path.name}: {e}")
        return None


def run_all_queries(conn):
    """Execute all SQL queries and export results."""
    logger.info("=" * 60)
    logger.info("Running all SQL queries")
    logger.info("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all query files
    query_files = sorted(glob(str(QUERIES_DIR / "*.sql")))

    logger.info(f"Found {len(query_files)} query files")

    results = {}
    for query_file in query_files:
        query_path = Path(query_file)
        output_path = OUTPUT_DIR / f"{query_path.stem}.csv"

        result_df = execute_query(conn, query_path, output_path)
        if result_df is not None:
            results[query_path.stem] = result_df

    logger.info("=" * 60)
    logger.info(f"Completed {len(results)} queries successfully")
    logger.info("=" * 60)

    return results


def show_sample_results(results: dict):
    """Show sample results from key queries."""
    logger.info("\n" + "=" * 60)
    logger.info("Sample Results")
    logger.info("=" * 60)

    # Show top 3 results from a few key queries
    key_queries = ['01_median_rent_by_locality', '05_rent_by_station_distance', '08_regional_comparison']

    for query_name in key_queries:
        if query_name in results:
            df = results[query_name]
            logger.info(f"\n{query_name} (first 5 rows):")
            logger.info(df.head().to_string(index=False))


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("SQL Query Runner")
    logger.info("=" * 60)

    # Create database
    conn = create_database()

    # Run all queries
    results = run_all_queries(conn)

    # Show sample results
    show_sample_results(results)

    # Close connection
    conn.close()
    logger.info("Database connection closed")

    logger.info("\n" + "=" * 60)
    logger.info("Query execution complete")
    logger.info("=" * 60)
    logger.info(f"Results saved to {OUTPUT_DIR}")

    return results


if __name__ == "__main__":
    main()
