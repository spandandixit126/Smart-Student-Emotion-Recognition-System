import glob
import os
import json

# custom modules
import call_model


def main(vid):
    owd = os.getcwd()
    li = []
    vid_dir = "video_frames/" + vid
    os.chdir(vid_dir)
    for file in glob.glob("*.jpg"):
        print("getting file...", file)
        li.append(str(file))
    os.chdir(owd)
    print("files founded:", li)

    data = {'emotions': []}
    for i in range(len(li)):
        pred = call_model.main(li[i])
        data['emotions'].append({'happy': f"{pred[0][0]:.4f}",
                                 'sad': f"{pred[0][1]:.4f}",
                                 'angry': f"{pred[0][2]:.4f}",
                                 'neutral': f"{pred[0][3]:.4f}"
                                 })

    data_copy = data
    data = {'emotions': []}
    return data_copy
    '''with open(vid_dir+"/emotions.json", 'w') as outfile:
        json.dump(data, outfile)'''
