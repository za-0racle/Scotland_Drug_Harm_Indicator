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
 backtest:['model','origin','target','predicted','lower80','upper80','lower95','upper95'],
 forecast:['model','forecast_origin','target_period','predicted','lower80','upper80','lower95','upper95'],
};
export const researchHeadings={origin:'Training through',target:'Target quarter',observation_period:'Quarter',mae:'Mean absolute error (source units)',rmse:'Root mean squared error (source units)',evaluated_origins:'Evaluation targets',coverage80:'80% interval coverage (proportion)',coverage95:'95% interval coverage (proportion)',statistic_value:'Stored monitoring statistic',signal_flag:'Stored flag',cusum_positive:'Positive CUSUM component',cusum_negative:'Negative CUSUM component',lower_limit:'Stored lower limit',upper_limit:'Stored upper limit',lower80:'80% lower bound',upper80:'80% upper bound',eligible_choices:'Eligible settings',signal_choices:'Settings with a flag',signal_fraction:'Proportion of eligible settings flagged',signals99:'Flags outside 99% intervals',signal_frequency99:'Flag proportion',coverage99:'99% interval coverage (proportion)',evaluated:'Evaluated observations'};
export const monitoringCopy={
 stored:'Original results include rolling Negative Binomial residual monitoring with EWMA and a separate opioid-share CUSUM. EWMA (exponentially weighted moving average) gives more weight to recent residuals. CUSUM (cumulative sum) tracks accumulated departures; its positive and negative components are separate. The CUSUM zero lower limit is a reset baseline, not a lower alarm limit. Select a row for its complete record.',
 configurations:'Original monitoring configurations describe the rolling Negative Binomial baseline and the EWMA and CUSUM settings. They are not the later Negative Binomial moments comparator or the forecasting trend model.',
 flags:'Additional historical screens compare observations with earlier medians and median absolute deviations (MAD). Conditional count-model comparisons use separate assumptions. Each flag identifies an unusual observation under its selected method; review its source, period and direction.',
 context:'Review all stored observations for the selected scope, including each original flag and classification. Results retain the saved source values.',
 sensitivity:'Compare how results change across six parameter settings. This analysis describes parameter stability across the tested configurations.',
 models:'Compare how conditional count models describe recorded values. These results are reported separately from the original monitoring methods and forecast evaluation.',
 diagnostics:'Review model checks against earlier observations, including sparse histories and correlated series.',
 zero:'Review how unknown geography and sparse counts are classified in the source records.',
 runs:'Consecutive flagged periods are grouped within each series, method and direction.',
 evidence:'Supporting observations retain their original source populations and reporting periods. Compare these records side by side with their source definitions.',
 validation:'The PHS FOI response and archived alert publications are stored for retrospective research. This view records archive receipt and live-feed status; the version history provides the published alert chronology.',
};
export const forecastEvaluation='Each prediction used only earlier quarters in the dataset. Four candidates share 12 quarterly targets (2023 Q1–2025 Q4), with an expanding training window. Mean absolute error (MAE) is the average absolute prediction error, in deaths; lower is better. The last-observation baseline was selected and scored on the same targets, so these scores describe this retrospective evaluation set. Interval calibration and historical data vintages are documented with the results.';
export function projectionText(row){
 return `Historical-origin estimate for ${row.target_period}, based on observations through ${row.forecast_origin}: ${row.predicted} deaths. Approximate 80% observation interval: ${row.lower80} to ${row.upper80}; 95% observation interval: ${row.lower95} to ${row.upper95}.`;
}

export function forecastFinding(rows){
 const baseline=rows.find(row=>row.model==='naive');
 return rows.length===4&&rows.every(row=>row.evaluated_origins===12&&Number.isFinite(row.mae))&&baseline&&rows.every(row=>row.mae>=baseline.mae)?`The last-observation baseline had the lowest mean absolute error: ${baseline.mae.toFixed(2)} deaths across 12 common quarterly targets. The baseline was selected and scored on the same targets; this is retrospective performance on the recorded evaluation set.`:'Compare the four saved candidate scores across their common evaluation targets. Select a row to inspect the complete metrics.';
}
