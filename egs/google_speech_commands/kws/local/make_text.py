#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from glob import glob


def run_shell(cmd, log_file=None):
    if cmd.split(" ")[0].endswith(".sh"):
        if not (os.path.isfile(cmd.split(" ")[0]) and os.access(cmd.split(" ")[0], os.X_OK)):
            print("WARNING: {} does not exist or is not runnable!".format(cmd.split(" ")[0]))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    (output, err) = p.communicate()
    return_code = p.wait()
    if return_code > 0:
        raise RuntimeError("Failed to call: {} \n Error return code: {}".format(cmd, return_code))
    if log_file is not None:
        with open(log_file, 'a+') as logfile:
            logfile.write(output.decode("utf-8") + '\n')
            logfile.write(err.decode("utf-8") + '\n')
    else:
        print(output.decode("utf-8"))
        print(err.decode("utf-8"), file=sys.stderr)
    return output


def task_done(data_dir, train_dir, dev_dir, test_dir):
    return os.path.exists(os.path.join(data_dir, train_dir, "spk2utt")) and \
           os.path.exists(os.path.join(data_dir, train_dir, "text")) and \
           os.path.exists(os.path.join(data_dir, train_dir, "utt2spk")) and \
           os.path.exists(os.path.join(data_dir, train_dir, "wav.scp")) and \
           os.path.exists(os.path.join(data_dir, dev_dir, "spk2utt")) and \
           os.path.exists(os.path.join(data_dir, dev_dir, "text")) and \
           os.path.exists(os.path.join(data_dir, dev_dir, "utt2spk")) and \
           os.path.exists(os.path.join(data_dir, dev_dir, "wav.scp")) and \
           os.path.exists(os.path.join(data_dir, test_dir, "spk2utt")) and \
           os.path.exists(os.path.join(data_dir, test_dir, "text")) and \
           os.path.exists(os.path.join(data_dir, test_dir, "utt2spk")) and \
           os.path.exists(os.path.join(data_dir, test_dir, "wav.scp"))


def create_text_transcript_file(speech_commands_dir, data_dir):
    train_dir = "train"
    dev_dir = "dev"
    test_dir = "test"

    if not task_done(data_dir, train_dir, dev_dir, test_dir):

        with open(os.path.join(speech_commands_dir, "validation_list.txt"), "r") as dev_f:
            dev_list = dev_f.readlines()

        with open(os.path.join(speech_commands_dir, "testing_list.txt"), "r") as test_f:
            test_list = test_f.readlines()

        wav_files = glob(os.path.join(speech_commands_dir, "*", "*.wav"))

        def match(wav_file):
            command = os.path.basename(os.path.dirname(wav_file))
            utterance_id = os.path.basename(wav_file).replace("nohash", command).replace(".wav", "")
            text = command
            speaker_id = utterance_id.split("_")[0]
            path = os.path.join(speech_commands_dir, os.path.basename(os.path.dirname(wav_file)), os.path.basename(wav_file))
            path = os.path.abspath(path)
            assert os.path.exists(path)
            return utterance_id, text, speaker_id, path

        all_files = [match(wav_file) for wav_file in wav_files]
        test_files = [match(wav_file.strip()) for wav_file in test_list]
        dev_files = [match(wav_file.strip()) for wav_file in dev_list]

        train_files = list(set(all_files) - set(test_files) - set(dev_files))

        train_files.sort(key=lambda x: x[0])
        dev_files.sort(key=lambda x: x[0])
        test_files.sort(key=lambda x: x[0])

        if not os.path.exists(os.path.join(data_dir, train_dir)):
            os.mkdir(os.path.join(data_dir, train_dir))

        if not os.path.exists(os.path.join(data_dir, dev_dir)):
            os.mkdir(os.path.join(data_dir, dev_dir))

        if not os.path.exists(os.path.join(data_dir, test_dir)):
            os.mkdir(os.path.join(data_dir, test_dir))

        # text

        with open(os.path.join(data_dir, train_dir, "text"), "w") as train_text_f:
            train_text_f.writelines([line[0] + " " + line[1] + "\n" for line in train_files])

        with open(os.path.join(data_dir, dev_dir, "text"), "w") as dev_text_f:
            dev_text_f.writelines([line[0] + " " + line[1] + "\n" for line in dev_files])

        with open(os.path.join(data_dir, test_dir, "text"), "w") as test_text_f:
            test_text_f.writelines([line[0] + " " + line[1] + "\n" for line in test_files])

        # utt2spk

        with open(os.path.join(data_dir, train_dir, "utt2spk"), "w") as train_utt2spk_f:
            train_utt2spk_f.writelines([line[0] + " " + line[2] + "\n" for line in train_files])

        with open(os.path.join(data_dir, dev_dir, "utt2spk"), "w") as dev_utt2spk_f:
            dev_utt2spk_f.writelines([line[0] + " " + line[2] + "\n" for line in dev_files])

        with open(os.path.join(data_dir, test_dir, "utt2spk"), "w") as test_utt2spk_f:
            test_utt2spk_f.writelines([line[0] + " " + line[2] + "\n" for line in test_files])

        # wav.scp

        with open(os.path.join(data_dir, train_dir, "wav.scp"), "w") as train_wav_scp_f:
            train_wav_scp_f.writelines([line[0] + " " + line[3] + "\n" for line in train_files])

        with open(os.path.join(data_dir, dev_dir, "wav.scp"), "w") as dev_wav_scp_f:
            dev_wav_scp_f.writelines([line[0] + " " + line[3] + "\n" for line in dev_files])

        with open(os.path.join(data_dir, test_dir, "wav.scp"), "w") as test_wav_scp_f:
            test_wav_scp_f.writelines([line[0] + " " + line[3] + "\n" for line in test_files])

        run_shell("utils/utt2spk_to_spk2utt.pl {}/{}/utt2spk > {}/{}/spk2utt"
                  .format(data_dir, train_dir, data_dir, train_dir))



        run_shell("utils/utt2spk_to_spk2utt.pl {}/{}/utt2spk > {}/{}/spk2utt"
                  .format(data_dir, dev_dir, data_dir, dev_dir))

        run_shell("utils/utt2spk_to_spk2utt.pl {}/{}/utt2spk > {}/{}/spk2utt"
                  .format(data_dir, test_dir, data_dir, test_dir))

        print("Preparing directory done!")

    else:
        print("Directory already prepared! Skipping...")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='#TODO')
    parser.add_argument('speech_commands_dir', metavar='PATH', type=str,
                        help='path to the speech commands directory')
    parser.add_argument('data_dir', metavar='PATH', type=str,
                        help='path where the extracted dataset should be')

    args = parser.parse_args()
    create_text_transcript_file(args.speech_commands_dir, args.data_dir)

# http://kaldi-asr.org/doc/data_prep.html#data_prep_data
