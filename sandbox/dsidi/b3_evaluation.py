# UA B3 Project - Evaluation code
#
# Assumptions: There is no index 0 indicating that an activity is performed. Don't zero index the activities!
# Currently handles just the presence of individual walks. TODO groups
# notes:
#   This script must reside in the directory where the data file is found. TODO right (from other script)?
#
# author: dsidi
# created: 17 Mar 2014
# filename: b3_evaluation.py

import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import takewhile
import os
import sys
import b3_evaluation

class b3_evaluator:

    def __init__(self, b3_filename, gt_filename, cwd=None):
        """
        Reads in a sequence of CSV files representing frame-by-individual matrices for each activity.
        Currently, activities include:

            Physical
            ========
            - stand
            - walk
            - run

            Intentional1
            ============
            - move_to

            Intentional2
            =============
            - meet

        Notes: currently does not chunk the input (this can be added as needed)
        """
        #TODO make these local
        self._gt_rel_path = ''
        self._b3_rel_path = ''
        # todo rm params (now iterates the current dir)


        #generate all pairs of b3-gt activity csvs
        if not cwd:
            cwd = os.getcwd()

        b3_abs_file_path = os.path.join(cwd, self._b3_rel_path, b3_filename)
        gt_abs_file_path = os.path.join(cwd, self._gt_rel_path, gt_filename)

        #fills b/c NaN's compare to False
        self.gt_reader = pd.read_csv(gt_abs_file_path, index_col=0).fillna(0)
        self.b3_reader = pd.read_csv(b3_abs_file_path, index_col=0).fillna(0)

        #DEBUG
        #print self.gt_reader
        #print self.b3_reader


    def identify_activities(self, reader):
        """
        Used to find the intervals of activities for different individuals in the GT and B3 data.
        We need both the frame interval of the action, and the individuals participating at each
        frame. The index of the action will not match between GT and B3, but obviously they should match
        within these.
        ASSUMPTIONS: groups are sets (i.e., their identity is uniquely determined by their members).
        Since activity id's will not match, we need to map the list of activity id's in which each
        individual participates to the members participating in that activity. These members can then
        be compared b/w B3 and GT.

        TODO handle partial overlaps, as in cases where GT has a single activity (call it `17'), but the B3
        has two activities (call them 'a' and 'b') where 'a' has all members of '17' except person 1, and 'b' has
        just person 1 in it, with 'b' starting the frame after 'a' ends. This shouldn't just be a false negative
        and a false positive.
        UPDATE: this will be done by asking at each frame whether the group is correct.
        Given the possibly large number of frames, this pushes us to use of generators.
        """
        #gt_activities = gt_reader.apply(pd.Series.value_counts, axis=1).fillna(0).transpose() #we need identities of
        # individuals, not just a number of individuals. So this is not very useful...

        #Currently unused
        raise Exception('not implemented!')

        # acts_of_person, group_of_act = defaultdict(list), defaultdict(list)  #naming convention has <target>_of_<source>
        #
        #
        #
        #     for k in acts_at_a_frame.groupby(acts_at_a_frame.values).groups:
        #         if len()
        #     if contig_act != []:
        #         # currently not used beyond getting the act_id. Kept for possible future relaxation of assn's.
        #         first_frame = contig_act.index[0]
        #         last_frame = first_frame + \
        #                      len([j for j in takewhile(lambda x: x>0, contig_act.ix[first_frame:])])-1
        #
        #         person_id = i
        #         act_id = contig_act[first_frame]
        #         acts_of_person[person_id].append(act_id)
        #         group_of_act[act_id].append(person_id) # don't need the interval, since act_id's determine them
        #         #   (see ASSUMPTIONS in the function comment above)
        #
        # return acts_of_person, group_of_act

    def group_precision_recall(self):
        """
        checks for contiguous frames in the ground truth (indicating an activity), then checks
        across individuals to see if the activity was pursued in a group.

        we want to be able to check that individuals are assigned to the correct group (and not just that
        they are in some group in the right interval).

        ASSUMPTIONS: no one is in distinct groups in a single frame.

        """
        gt_reader = self.gt_reader
        b3_reader = self.b3_reader
        tp, fp, tn, fn = 0, 0, 0, 0

        #TODO check for mismatched intervals?

        for frame in self.gt_reader.index:
            gt_acts_at_a_frame = self.gt_reader.ix[frame][gt_reader.ix[frame]>0]
            b3_acts_at_a_frame = self.b3_reader.ix[frame][b3_reader.ix[frame]>0]

            # create an encoding (a dict) to allow comparison even with differently named activities
            gt_group = gt_acts_at_a_frame.groupby(gt_acts_at_a_frame.values).groups
            b3_group = b3_acts_at_a_frame.groupby(b3_acts_at_a_frame.values).groups

            for gt_activity_group in gt_group.itervalues():
                # search for even partial matches of each group in the frame by checking the
                # intersection
                group_fp, group_fn, group_tp, group_tn = 0, 0, 0, 0
                for b3_activity_group in b3_group.itervalues():
                    b3_activity_group = set(b3_activity_group)
                    gt_activity_group = set(gt_activity_group)

                    if gt_activity_group.intersection(b3_activity_group):
                        group_fp = len(b3_activity_group - gt_activity_group) #set difference
                        group_fn = len(gt_activity_group - b3_activity_group) #set difference
                        group_tp = len(b3_activity_group) - group_fp
                        break
                fn += group_fn
                fp += group_fp
                tp += group_tp
                tn += (len(gt_reader.ix[frame]) - (group_tp+group_fn)) - group_fp

        precision = float(tp) / (tp + fp) #TODO extract these to functions
        recall = float(tp) / (tp + fn)

        return precision, recall

        #______________________________
        #
        # BEGIN EXTRA STUFF FOR THIS FN
        #______________________________
        #

        # gt_acts_of_person, gt_group_of_act = self.identify_activities(self.gt_reader)
        # b3_acts_of_person, b3_group_of_act = self.identify_activities(self.b3_reader)
        # tp,fp,tn,fn = 0,0,0,0
        # #TODO check for key mismatch
        # for gt_person_id in self.gt_reader_t.index:
        #     # check groups that each person is involved with
        #     for group in [gt_group_of_act[act] for act in gt_acts_of_person[gt_person_id]]:
        #         if group in [b3_group_of_act[act] for act in b3_acts_of_person[gt_person_id]]:
        #             tp +=1
        #         else:
        #             fn +=1
        #
        #
        #
        #     p_rs.append(compare_b3(nxt_activity)) # store precision-recall for this activity based on b3 data
        #
        #
        # gt_activityStarts = gt_reader.apply(pd.Series.first_valid_index, axis=0)
        # b3_activityStarts = b3_reader.apply(pd.Series.first_valid_index, axis=0)
        #
        # matchCounts = np.count_nonzero(gt_activityCounts == b3_activityCounts)
        # matchStarts = np.count_nonzero(gt_activityStarts == b3_activityStarts)
        # earliestActivity = reader_t.apply(pd.Series.first_valid_index, axis=1).fillna(0) # idx by indiv. number
        #
        # #get facts about group activities: a group activity in the ground truth
        # # has a count of more than one individual in a frame
        # gt_activities = gt_reader.apply(pd.Series.value_counts, axis=1).fillna(0).transpose()
        #
        # for activity_idx in gt_activities.index:
        #     activity = gt_activities.ix[activity_idx]
        #
        # gt_activities = gt_activityCounts.apply(lambda x: x > 1, axis=0) # find groups of more than 1
        #
        #
        # b3_activityCounts = b3_reader.apply(pd.Series.value_counts, axis=1).transpose()


    def physical_precision_recall(self):
        """
        computes the precision and recall for the B3 output
            precision: tp / (tp + fp)
            recall: tp / (tp + fn)
        """
        gt_reader = self.gt_reader
        b3_reader = self.b3_reader

        gt_val = gt_reader.values
        b3_val = b3_reader.values

        # use nonzero since indices won't match
        #TODO this might require some preliminary data treatment to make sure nonactivities are counted properly
        #TODO   seems to work for 'A','B', ... activity labels as well as number activity labels
        tp = np.count_nonzero((b3_val != 0) & (gt_val != 0))
        tn = np.count_nonzero((b3_val == 0) & (gt_val == 0))
        fp = np.count_nonzero((b3_val != 0) & (gt_val == 0))
        fn = np.count_nonzero((b3_val == 0) & (gt_val != 0))

        if (tp+fp <= 0 or tp+fn <= 0):
            raise Exception("Cannot compute precision and recall: div. by zero")

        precision = float(tp) / (tp + fp)
        recall = float(tp) / (tp + fn)

        #DEBUG
        #print np.array_equal(gt_activityCounts.values,b3_activityCounts.values)
        #print np.array_equal(gt_activityStarts.values,b3_activityStarts.values)
        #print "precision is: ", precision
        #print "recall is: ", recall

        return precision, recall


        #for col in reader.transpose()[1:].ix:
        #    # Get nonempty values TODO empty values are null, or 0?
        #    #TODO do something nicer here
        #    checks = dict()
        #    for i in col[1:].ix:
        #        activityFrames = i[i.notnull()][1:].index #indices of the frames in which activities occur
        #        if activityFrames != []:
        #            minIdx = min(activityFrames)
        #            minVal = i[min(activityFrames)] # this is the val. of the first activity found in this col
        #            checks[minIdx] = minVal
        #            for j in col[1:]:
        #                if j[minIdx] == minVal: activities.append(j[0]) # append individual number for matches

        ##now check rows for a match
        #for k in checks.iterkeys():
        #    selected_rows = reader.ix[k]
        #    selected_rows[selected_rows == selected_rows[k]]



def generate_csv_pair(data_dir):
    """
    get all csv's in the directory of this file
    TODO fix use of data_dir (artifact of laziness)
    """
    _b3_suffix = '_b3'
    _gt_suffix = '_gt'
    curr_dir_csvs = [x for x in os.listdir(data_dir) if x.endswith('.csv')]

    for filename in curr_dir_csvs:
        # get all filenames matching except for suffixed `_b3' / `_gt'
        filename,_ = os.path.splitext(filename)
        if filename.endswith(_b3_suffix):
            b3_filename = filename + '.csv'
            gt_filename = b3_filename.replace(_b3_suffix, _gt_suffix)
            #print (b3_filename, gt_filename, basename)
            yield (b3_filename, gt_filename)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        cwd = sys.argv[1]
    else:
        cwd = os.path.dirname(__file__)

    p_r = defaultdict(list)

    print 'using data in', cwd
    for b3,gt in b3_evaluation.generate_csv_pair(cwd):
        a = b3_evaluator(b3, gt, cwd)
        filename_base = gt.replace('.csv','').replace('_gt','')
        print 'Now evaluating: {}'.format(filename_base)
        if filename_base in ['walk','stand','run']:
            p_r[filename_base].append(a.physical_precision_recall())
        else:
            p_r[filename_base].append(a.group_precision_recall())

        print "\n"
        print p_r
