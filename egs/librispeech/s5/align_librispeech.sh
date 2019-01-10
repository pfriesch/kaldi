#!/usr/bin/env bash
. ./cmd.sh ## You'll want to change cmd.sh to something that will work on your system.
. ./path.sh ## Source the tools/utils (import the queue.pl)

chunk=train_clean_100
#chunk=dev_clean # Uncomment to process dev
#chunk=test_clean # Uncomment to process test
gmmdir=/mnt/data/libs/kaldi/egs/timit/s5/exp/tri4_nnet

dir=fmllr/$chunk
steps/nnet/make_fmllr_feats.sh --nj 10 --cmd "$train_cmd" \
    --transform-dir $gmmdir/decode_tgsmall_$chunk \
        $dir data/$chunk $gmmdir $dir/log $dir/data || exit 1
        
compute-cmvn-stats --spk2utt=ark:data/$chunk/spk2utt scp:fmllr/$chunk/feats.scp ark:$dir/data/cmvn_speaker.ark