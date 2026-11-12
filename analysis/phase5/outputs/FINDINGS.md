# Phase 5 execution findings

Primary screens: 8034 observations; 47 statistical flags. Classifications: {'insufficient_data': 2262, 'no_detected_anomaly': 5717, 'statistically_unusual_observation': 47, 'unavailable_analysis': 8}.

Historical evidence: {'insufficient_evidence': 2270, 'no_detected_signal': 5717, 'single_indicator_signal': 47}.

Sensitivity: {'insufficient_data': 1168, 'no_signal_in_eligible_choices': 6495, 'choice_sensitive': 198, 'all_choices_same_direction_signal': 17}.

All flags are retrospective research screens. See anomaly_results.csv for every flag, threshold, baseline, exact period and source.

## National-series flags (all)

| Dataset | Geography | Period | Observed | Prior median | Lower | Upper | Direction |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |

## Flags by dataset

- mortality_quarterly: 3 flags; {'insufficient_data': 240, 'no_detected_anomaly': 253, 'statistically_unusual_observation': 3, 'unavailable_analysis': 8}.
- forensic_counts: 11 flags; {'insufficient_data': 112, 'no_detected_anomaly': 87, 'statistically_unusual_observation': 11}.
- treatment_counts: 0 flags; {'insufficient_data': 90, 'no_detected_anomaly': 50}.
- naloxone_weekly: 33 flags; {'insufficient_data': 1664, 'no_detected_anomaly': 5327, 'statistically_unusual_observation': 33}.
- assist_percentages: 0 flags; {'insufficient_data': 72}.
- frozen_forensic_shares: 0 flags; {'insufficient_data': 84}.

## Limits and next decision

- No seasonal/trend adjustment, testing-volume/exposure adjustment or as-published vintages
- Serial correlation, overlapping windows, repeated comparisons and sample changes may produce flags
- Count-scale floor is a pragmatic safeguard, not a fitted count distribution; low-count screens may be conservative
- No reference event set: signal frequency is not false-positive rate, sensitivity, specificity or lead time
- Exact domains/geographies/periods prevent cross-source corroboration in these inputs; absence of support is not absence of harm
- ASSIST and frozen shares are not forced into new statistical models; no private RADAR narratives read
- All findings retrospective; historical flags are not confirmed public health alerts

No compatible multi-source corroboration or current early warning is established. Preserve original historical monitoring independently. Stop after Phase 5; next consider a separately approved methods review and source-vintage/denominator harmonisation, before any publication or interface work.
