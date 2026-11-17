export const researchColumns={
 flags:['geography','indicator_id','period','method','observed_value','baseline_estimate','lower_threshold','upper_threshold','classification','signal_direction'],
 enhanced:['geography','indicator_id','period','method','observed_value','baseline_estimate','lower99','upper99','classification','signal_direction'],
 sensitivity:['geography','indicator_id','period','eligible_choices','signal_choices','signal_fraction','stability'],
 models:['geography','indicator_id','method','evaluated','mae','coverage99','signals99','signal_frequency99'],
 diagnostics:['observation_id','method','window','reference_start','reference_end','mean','variance','dispersion','status'],
 runs:['geography','indicator_id','method','configuration','start','end','direction','duration_periods','classification'],
 stored:['configuration_label','observation_period','statistic_value','lower_limit','upper_limit','signal_flag','cusum_positive','cusum_negative'],
 configurations:['configuration_label','method','baseline_description','rolling_window_quarters','lambda_value','limit_multiplier','cusum_k_sigma','cusum_h_sigma','notes'],
 forecastModels:['model','mae'],
 forecast:['model','forecast_origin','target_period','predicted','lower80','upper80','lower95','upper95'],
};
export const researchHeadings={observation_period:'Quarter',mae:'Mean absolute error (source units)',rmse:'Root mean squared error (source units)',evaluated_origins:'Evaluation targets',coverage80:'80% interval coverage (proportion)',coverage95:'95% interval coverage (proportion)',statistic_value:'Stored monitoring statistic',signal_flag:'Stored flag',cusum_positive:'Positive CUSUM component',cusum_negative:'Negative CUSUM component',lower_limit:'Stored lower limit',upper_limit:'Stored upper limit',lower80:'80% lower bound',upper80:'80% upper bound',eligible_choices:'Eligible settings',signal_choices:'Settings with a flag',signal_fraction:'Proportion of eligible settings flagged',signals99:'Flags outside 99% intervals',signal_frequency99:'Flag proportion',coverage99:'99% interval coverage (proportion)',evaluated:'Evaluated observations'};
export const monitoringCopy={
 stored:'Original results include rolling Negative Binomial residual monitoring with EWMA and a separate opioid-share CUSUM. EWMA (exponentially weighted moving average) gives more weight to recent residuals. CUSUM (cumulative sum) tracks accumulated departures; its positive and negative components are separate. The CUSUM zero lower limit is a reset baseline, not a lower alarm limit. Select a row for its complete record.',
 configurations:'Original monitoring configurations describe the rolling Negative Binomial baseline and the EWMA and CUSUM settings. They are not the later Negative Binomial moments comparator or the forecasting trend model.',
 flags:'Additional historical screens: the median-based screen compares observations with earlier medians and median absolute deviations (MAD). Conditional count-model comparisons use different assumptions. A statistical flag is an unusual historical observation under one method, not a confirmed toxicity incident.',
 context:'All stored observations for the selected scope, including flagged, non-flagged, insufficient-history and unavailable classifications. No flags are added or recalculated.',
 sensitivity:'How results change across six parameter settings. This is parameter sensitivity, not sensitivity for detecting externally verified events.',
 models:'How well the conditional count models describe recorded values. These later comparisons are distinct from the original rolling Negative Binomial monitoring and from forecasting. Flag frequencies are not operational false-alarm rates.',
 diagnostics:'Checks on the earlier observations used by each model. Sparse history and correlated series limit interpretation; diagnostics do not establish warning performance.',
 zero:'Unknown geography and sparse-count checks retain their original classifications. Missing or unassigned observations do not establish absence of harm.',
 runs:'Consecutive flagged periods form a run within one series, method and direction. Runs and overlapping series are not separate confirmed incidents.',
 evidence:'Supporting observations from different sources retain their own populations and reporting periods. Co-occurrence does not establish a shared incident or causal relationship.',
 validation:'External validation remains pending. Missing official-alert records are not no-alert periods. Detection sensitivity, specificity and lead time have not been validated.',
};
export const forecastEvaluation='Each prediction used only earlier quarters in this retrospective dataset. Four candidates share 12 quarterly targets (2023 Q1–2025 Q4), with an expanding training window. Mean absolute error (MAE) is the average absolute prediction error, in deaths; lower is better. The last-observation baseline was selected using these same targets, so there is no independent post-selection test. Twelve targets cannot establish reliable interval calibration; revised data are not necessarily the values available at the time.';
export function projectionText(row){
 return `Saved estimate for ${row.target_period}, based on observations through ${row.forecast_origin}: ${row.predicted} deaths. Saved approximate 80% observation interval: ${row.lower80} to ${row.upper80}; 95% observation interval: ${row.lower95} to ${row.upper95}. The target period has elapsed. Not a current future prediction.`;
}

export function forecastFinding(rows){
 const baseline=rows.find(row=>row.model==='naive');
 return rows.length===4&&rows.every(row=>row.evaluated_origins===12&&Number.isFinite(row.mae))&&baseline&&rows.every(row=>row.mae>=baseline.mae)?`The last-observation baseline had the lowest mean absolute error: ${baseline.mae.toFixed(2)} deaths across 12 common quarterly targets. These targets were also used to select the model; this is not an independent test.`:'Compare saved candidate errors on their recorded evaluation targets. Select a row to inspect the complete metrics.';
}
