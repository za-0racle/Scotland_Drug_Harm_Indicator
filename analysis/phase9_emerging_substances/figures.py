"""Deterministic static research plots; no inferred observations or warning metrics."""
from datetime import datetime
import os
from pathlib import Path
_cache=Path(__file__).resolve().parents[1]/'test_scratch.local'/'phase9_matplotlib'
_cache.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(_cache))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
from .analyse import SELECTED

def figures(rows,changes,events,directory):
    directory.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'phase9-fixed','svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    def series(label,sheet='SUB1a'):
        return sorted([r for r in rows if r['vintage']=='2024' and r['sheet']==sheet and r['substance_label']==label and r['year']>=2008],key=lambda r:r['year'])
    def save(fig,name,note):
        fig.text(.02,.015,note,fontsize=8,va='bottom');fig.tight_layout(rect=(0,.10,1,.94))
        fig.savefig(directory/(name+'.svg'),metadata={'Date':None});fig.savefig(directory/(name+'.png'),dpi=220,metadata={'Software':'Phase 9 / Matplotlib'})
        plt.close(fig)
    note='Source: NRS individual-substance workbook, 2024 edition (published 2 September 2025), SUB1a.\nCounts overlap across drugs; not prevalence, first discovery, causation or real-time warnings. Testing changed over time.'
    selected=SELECTED[:4];fig,axes=plt.subplots(2,2,figsize=(12,8))
    for ax,label in zip(axes.flat,selected):
        data=series(label);ax.bar([r['year'] for r in data],[r['count'] if r['count'] is not None else np.nan for r in data],color='#087f83');ax.set_title(label.title());ax.set_ylabel('Registered deaths involving substance');ax.set_xlabel('Registration year');ax.set_xticks([2008,2012,2016,2020,2024])
    fig.suptitle('Recorded involvement: implicated or potentially contributing, drug misuse deaths, Scotland')
    save(fig,'01_annual_selected',note)
    fig,ax=plt.subplots(figsize=(12,7));positions=np.arange(len(SELECTED))
    for i,year in enumerate((2023,2024)):
        values=[next((r['count'] for r in series(label) if r['year']==year),np.nan) for label in SELECTED]
        ax.barh(positions+(i-.5)*.36,values,height=.36,label=str(year),color=['#42699b','#087f83'][i])
    ax.set_yticks(positions,[s.title() for s in SELECTED]);ax.set_xlabel('Registered drug misuse deaths: implicated / potentially contributing');ax.legend(title='Registration year');ax.set_title('Separate substances, common reporting definition: Scotland, 2023 and 2024')
    save(fig,'02_selected_comparison',note+'\nSelection includes four requested substances plus etizolam, diazepam and isotonitazene for contextual contrast; bars are not additive.')
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for ax,label in zip(axes.flat,selected):
        data=[r for r in changes if r['vintage']=='2024' and r['sheet']=='SUB1a' and r['substance_label']==label and r['year']>=2019];ax.bar([r['year'] for r in data],[r['annual_change'] if r['annual_change'] is not None else np.nan for r in data],color=['#42699b' if (r['annual_change'] or 0)<0 else '#087f83' for r in data]);ax.axhline(0,color='#334455',linewidth=.7);ax.set_title(label.title());ax.set_ylabel('Change from preceding registration year');ax.set_xlabel('Registration year')
    fig.suptitle('Annual changes in recorded implicated involvement, Scotland, 2019-2024')
    save(fig,'03_annual_changes',note+'\nUndefined changes are omitted; no statistical significance or validated threshold is implied.')
    fig,axes=plt.subplots(2,1,figsize=(13,8),sharex=True)
    comm=[e for e in events if e['type']=='original_official_issue']
    for i,e in enumerate(comm):
        t=datetime.fromisoformat(e['date']);axes[0].scatter(t,i,color='#087f83',s=55);axes[0].annotate(e['subject']+'\n'+e['date'],(t,i),xytext=(8,8),textcoords='offset points',fontsize=9)
    axes[0].set_ylim(-.5,3);axes[0].set_yticks([]);axes[0].set_title('Official original alert issue dates (not harm-onset dates)')
    for i,year in enumerate((2022,2023,2024)):
        start=dates.date2num(datetime(year,1,1));end=dates.date2num(datetime(year+1,1,1));axes[1].broken_barh([(start,end-start)],(i-.15,.3),facecolors='#42699b');axes[1].text(start+15,i+.2,f'{year} registration-year interval',fontsize=9)
    for e in events:
        if e['type']=='source_publication':
            t=datetime.fromisoformat(e['date']);axes[1].axvline(t,color='#96602d',linestyle='--');axes[1].annotate(e['date']+'\nNRS release',(t,2.6),rotation=45,fontsize=8)
    axes[1].set_ylim(-.5,4);axes[1].set_yticks([]);axes[1].set_title('Observation intervals versus later annual workbook publication');axes[1].xaxis.set_major_formatter(dates.DateFormatter('%b %Y'));axes[1].set_xlim(datetime(2022,1,1),datetime(2026,1,1));axes[1].set_xlabel('Calendar date (distinct clocks, no warning lead time)')
    save(fig,'04_communication_publication_timeline','Sources: NRS workbook covers; verified PHS original communications in outputs/communication_chronology.json.\nAnnual intervals are registration periods, not availability or exact death dates. Updates are separately recorded in the chronology; no event-performance metric.')
    fig,axes=plt.subplots(2,2,figsize=(12,8));sheets=('SUB1a','SUB1b','SUB2a','SUB2b')
    for ax,label in zip(axes.flat,selected):
        vals=[next((r['count'] for r in series(label,s) if r['year']==2024),np.nan) for s in sheets];ax.bar(sheets,vals,color=['#087f83','#84b9b7','#42699b','#a0b2cd']);ax.set_title(label.title());ax.set_ylabel('2024 registered deaths / mentions')
    fig.suptitle('Definition separation: Scotland, 2024 registration year')
    save(fig,'05_reporting_definitions','Source: NRS 2024 edition, published 2 September 2025. SUB1 = drug misuse; SUB2 = wider drug poisoning.\na = implicated / potentially contributing; b = present but not considered contributory. Do not sum sheets or substances.')
