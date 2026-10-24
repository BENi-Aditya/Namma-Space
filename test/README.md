# Test assets and provenance

`data/your-video.mov` is an exact copy of the existing `namma-space-project/input-videos/your-video.mov`, not synthetic data. SHA-256: `f3397deefd02eab8d255a14fa253334fb8cf6027f407460ff17227cd04680eee`. Size 14,331,095 bytes, duration 36.7 seconds, H.264 video 1280x720 at 30 fps. Raw audio is present in this original clip. Ownership, permission to publish interiors/audio and absence of personal information require owner review before public distribution. It is intentionally ignored until that review; provide a reviewed sample in this directory for the final code folder/repository.

This sample is associated with the historical baseline by filename only; a complete hash-linked training run was not found. It is not the source for IMG_2008. Its presence does not establish a fresh reproducible reconstruction.

`assets.json` records source/model hashes and local paths. Generated models are preserved locally and excluded from new Git additions; some historical mesh files were already tracked and remain so. No dummy public links or dummy models are substituted for real outputs.

Run `python3 -m unittest discover -s test -v`. These tests check non-overwrite guards, missing images/non-finite poses and manifest registration integrity. They do not prove reconstruction quality or browser performance.

## Distributable diagnostic excerpt

`data/tabletop-sample.mp4` is a real 8-second excerpt (seconds 4-12) from the baseline source, re-encoded at 640x360 with audio and metadata removed. It is 598,152 bytes; ffprobe confirms video only. Four evenly spaced frames were inspected: laptop/table, no visible people or personal documents in those sampled frames. This small derivative is included in Git. It demonstrates input format and the pipeline entry point; it is an object/tabletop capture, not evidence of a complete indoor room or the source of IMG_2008. Public sharing of the full original audio/interior capture is still not authorized by this derivative review.

Dry-run example on a Mac: `python scripts/pipeline/reconstruct.py test/data/tabletop-sample.mp4 sample-new --method nerfacto --device mps --iterations 500`. A full reconstruction of this diagnostic excerpt has not been verified.
