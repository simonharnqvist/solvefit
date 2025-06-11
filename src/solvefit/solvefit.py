import toml
import pulp
import click


def load_toml(path: str) -> tuple[dict, dict]:
    """Load activities data from TOML."""
    data = toml.load(path)
    activities = data["activities"]
    weights = data["weights"]
    return activities, weights


def make_categories(weights: dict) -> list[str]:
    return list(weights.keys())


def solve(activities: dict, weights: dict, n_sessions: int):
    """Solve Linear Programming optimisation problem"""
    prob = pulp.LpProblem("Training_Schedule_Optimization", pulp.LpMaximize)

    activity_sessions = {
        act: pulp.LpVariable(f"x_{act}", lowBound=0, cat="Integer")
        for act in activities
    }

    categories = make_categories(weights)

    prob += (
        pulp.lpSum(
            activity_sessions[act]
            * sum(activities[act].get(cat, 0) * weights[cat] for cat in categories)
            for act in activities
        ),
        "Total_Weighted_Score",
    )

    prob += pulp.lpSum(activity_sessions.values()) <= n_sessions, "Total_Session_Limit"

    for act, details in activities.items():
        if "max_sessions" in details:
            prob += (
                activity_sessions[act] <= details["max_sessions"],
                f"Max_sessions_{act}",
            )
        if "min_sessions" in details:
            prob += (
                activity_sessions[act] >= details["min_sessions"],
                f"Min_sessions_{act}",
            )

    prob.solve()
    return prob, activity_sessions


def print_results(
    prob: pulp.LpProblem,
    activities: dict[str, str],
    activity_sessions: dict[str, pulp.LpVariable],
):
    """Print results to console."""
    print(f"Status: {pulp.LpStatus[prob.status]}")
    print("\nRecommended training schedule:")
    for act in activities:
        print(f"  {act}: {int(activity_sessions[act].varValue)}")
    print(f"\nMaximum weighted score: {pulp.value(prob.objective):.3f}")


@click.command()
@click.option(
    "--n_sessions",
    type=click.IntRange(1, 7),
    default=5,
    help="Number of sessions in a week",
)
@click.option(
    "--toml-path",
    type=click.STRING,
    default="activities.toml",
    help="Path to TOML file defining activities",
)
def cli(toml_path: str, n_sessions: int):
    activities, weights = load_toml(toml_path)
    solution, activity_sessions = solve(activities, weights, n_sessions=n_sessions)
    print_results(
        prob=solution, activities=activities, activity_sessions=activity_sessions
    )
