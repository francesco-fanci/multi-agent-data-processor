import pandas as pd

from src.agents.base_agent import BaseAgent

from src.analytics.kpi import (update_incremental_speed)

from src.analytics.torque import (update_torque_statistics,update_daily_torque_statistics,calculate_torque_results,calculate_daily_torque_results,calculate_torque_moving_average,detect_torque_drift)

from src.analytics.anomaly import (update_torque_anomalies)

from src.analytics.idle import (detect_idle_periods,finalize_idle_period)

from src.analytics.correlation import (calculate_head_correlations,calculate_head_residual_correlations,find_top_correlations)

from src.config import (ANOMALY_IQR_MULTIPLIER,ANOMALY_MINIMUM_MARGIN,ANOMALY_MIN_EVENTS,IDLE_MIN_DURATION_SECONDS,IDLE_MAX_GAP_SECONDS,MOVING_AVERAGE_WINDOW_DAYS,DRIFT_WINDOW_DAYS,DRIFT_THRESHOLD,DRIFT_MIN_EVENTS,CORRELATION_MIN_EVENTS,CORRELATION_MIN_DAYS)

class AnalyticsAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="Analytics Agent",goal="Compute industrial telemetry analytics and KPIs")

    def run(self, context):

        required_keys = ["dataframe","events","clean_events"]

        for key in required_keys:
            if key not in context:
                raise ValueError("Missing " + key + " in context")

        dataframe = context["dataframe"]
        events = context["events"]
        clean_events = context["clean_events"]

        torque_stats = context.get("torque_stats",{})

        daily_torque_stats = context.get("daily_torque_stats",{})

        anomaly_stats = context.get("anomaly_stats",{})

        idle_state = context.get("idle_state")

        idle_periods = context.get("idle_periods",[])

        total_cycles = context.get("total_cycles",0)

        total_production_pieces = context.get("total_production_pieces",0)

        first_timestamp = context.get("first_timestamp")

        last_timestamp = context.get("last_timestamp")

        cycle_speed = context.get("cycle_speed",0.0)

        production_speed = context.get("production_speed",0.0)

        elapsed_seconds = context.get("elapsed_seconds",0.0)

        pending_cycles = context.get("pending_cycles",0)

        pending_production_pieces = context.get("pending_production_pieces",0)

        valid_events = events[events["Data Quality"] == "Valid"].copy()

        torque_events = valid_events[valid_events["Event Type"].isin(["Closure OK","Bad Closure"])].copy()

        update_torque_statistics(torque_stats,torque_events)

        update_daily_torque_statistics(daily_torque_stats,torque_events)

        update_torque_anomalies(anomaly_stats,torque_events,iqr_multiplier=(ANOMALY_IQR_MULTIPLIER),minimum_margin=(ANOMALY_MINIMUM_MARGIN),min_events=(ANOMALY_MIN_EVENTS))

        new_idle_periods, idle_state = (detect_idle_periods(dataframe,idle_state=idle_state,min_duration_seconds=(IDLE_MIN_DURATION_SECONDS),max_gap_seconds=(IDLE_MAX_GAP_SECONDS)))

        idle_periods = (idle_periods + new_idle_periods)

        new_cycles = clean_events["Count Difference"].sum()

        production_events = clean_events[clean_events["Event Type"].isin(["Closure OK","Bad Closure"])]

        new_production_pieces = (production_events["Count Difference"].sum())

        total_cycles += new_cycles

        total_production_pieces += (new_production_pieces)

        if len(clean_events) > 0:

            current_first = pd.to_datetime(clean_events["timestamp"].min())

            current_last = pd.to_datetime(clean_events["timestamp"].max())

            if first_timestamp is None:
                first_timestamp = current_first

            if (last_timestamp is None or current_last > pd.to_datetime(last_timestamp)):
                last_timestamp = current_last

            total_elapsed_seconds = (pd.to_datetime(last_timestamp) - pd.to_datetime(first_timestamp)).total_seconds()

            new_elapsed_seconds = (total_elapsed_seconds - elapsed_seconds)

            if new_elapsed_seconds <= 0:

                pending_cycles += new_cycles

                pending_production_pieces += (new_production_pieces)

            else:

                cycle_speed, _ = (update_incremental_speed(current_speed=cycle_speed,current_elapsed_seconds=(elapsed_seconds),new_pieces=(pending_cycles + new_cycles),new_elapsed_seconds=(new_elapsed_seconds)))

                production_speed, _ = (update_incremental_speed(current_speed=production_speed,current_elapsed_seconds=(elapsed_seconds),new_pieces=(pending_production_pieces+ new_production_pieces),new_elapsed_seconds=(new_elapsed_seconds)))

                pending_cycles = 0
                pending_production_pieces = 0

                elapsed_seconds = (total_elapsed_seconds)

        result = context.copy()

        result["torque_stats"] = torque_stats
        result["daily_torque_stats"] = (daily_torque_stats)
        result["anomaly_stats"] = anomaly_stats

        result["idle_state"] = idle_state
        result["idle_periods"] = idle_periods

        result["total_cycles"] = total_cycles
        result["total_production_pieces"] = (total_production_pieces)

        result["first_timestamp"] = (first_timestamp)
        result["last_timestamp"] = (last_timestamp)

        result["cycle_speed"] = cycle_speed
        result["production_speed"] = (production_speed)

        result["elapsed_seconds"] = (elapsed_seconds)

        result["pending_cycles"] = (pending_cycles)

        result["pending_production_pieces"] = (pending_production_pieces)

        return result
    
    def finalize(self, context):

        torque_results = calculate_torque_results(context.get("torque_stats",{}))

        daily_torque_results = (calculate_daily_torque_results(context.get("daily_torque_stats",{})))

        daily_torque_results = (calculate_torque_moving_average(daily_torque_results,window_days=(MOVING_AVERAGE_WINDOW_DAYS)))

        drift_results = detect_torque_drift(daily_torque_results,window_days=DRIFT_WINDOW_DAYS,threshold=DRIFT_THRESHOLD,min_events=DRIFT_MIN_EVENTS)

        correlation_matrix = (calculate_head_correlations(daily_torque_results,min_events=CORRELATION_MIN_EVENTS,min_days=CORRELATION_MIN_DAYS))

        residual_correlation_matrix = (calculate_head_residual_correlations(daily_torque_results,min_events=CORRELATION_MIN_EVENTS,min_days=CORRELATION_MIN_DAYS))

        top_correlations = find_top_correlations(correlation_matrix)

        top_residual_correlations = (find_top_correlations(residual_correlation_matrix))

        idle_periods = context.get("idle_periods",[]).copy()

        idle_state = context.get("idle_state")

        if idle_state is not None:

            idle_periods += finalize_idle_period(idle_state,min_duration_seconds=(IDLE_MIN_DURATION_SECONDS))

        result = context.copy()

        result["torque_results"] = (torque_results)

        result["daily_torque_results"] = (daily_torque_results)

        result["drift_results"] = (drift_results)

        result["correlation_matrix"] = (correlation_matrix)

        result["residual_correlation_matrix"] = residual_correlation_matrix

        result["top_correlations"] = (top_correlations)

        result["top_residual_correlations"] = top_residual_correlations

        result["idle_periods"] = (idle_periods)

        return result