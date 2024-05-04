import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def sync(source, dest):
    # 원본 폴더의 파일 사전
    # source_hashes = {}
    # for folder, _, files in os.walk(source):
    #     for fn in files:
    #         source_hashes[hash_file(Path(folder)) / fn] = fn

    # # 사본 폴더의 파일 사전
    # seen = set()
    # for folder, _, files in os.walk(dest):
    #     for fn in files:
    #         dest_path = Path(folder) / fn
    #         dest_hash = hash_file(dest_path)
    #         seen.add(dest_hash)
    #         # 원본 폴더에 없는 파일은 삭제
    #         if dest_hash not in source_hashes:
    #             dest_path.remove()
    #         # 원본과 이름이 다르면 옮바르게 수정
    #         elif dest_hash in source_hashes and fn != source_hashes[dest_hash]:
    #             shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])
    # # 원본에는 있지만 사본에는 없는 모든 파일을 사본으로 복사
    # for src_hash, fn in source_hashes.items():
    #     if src_hash not in seen:
    #         shutil.copy(Path(source) / fn, Path(dest) / fn)
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)
        if action == "MOVE":
            shutil.move(*paths)
        if action == "DELETE":
            os.remove(paths[0])


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


def determine_actions(source_hashes: dict, dst_hashes: dict, src_folder, dst_folder):
    for sha, filename in source_hashes.items():
        if sha not in dst_hashes:
            source_path = Path(src_folder) / filename
            dest_path = Path(dst_folder) / filename
            yield "copy", source_path, dest_path
        elif dst_hashes[sha] != filename:
            old_dest_path = Path(dst_folder) / dst_hashes[sha]
            new_dest_path = Path(dst_folder) / filename
            yield "move", old_dest_path, new_dest_path
    for sha, filename in dst_hashes.items():
        if sha not in source_hashes:
            yield "delete", dst_folder / filename


# 명시적 의존성 : https://sjquant.tistory.com/72
# mock : https://daco2020.tistory.com/482
