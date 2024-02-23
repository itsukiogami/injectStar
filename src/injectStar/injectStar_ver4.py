#!/usr/bin/env python3
# Inject the artificial stars into ~/HSC/rerun/<rerun>/deepCoadd/<filter>/<tract>/<patch>.fits
# ~/HSC/rerun/<rerun>/deepCoadd/<filter>/<tract>/<patch>/<patch>.fits に人工星を注入する

import lsst.afw.image as afwImage
import lsst.afw.geom as afwGeom
import lsst
#import lsst.geom as geom
import argparse
import glob
import numpy as np
import os
import sys
#sys.path.append('~/tqdm')
#from tqdm import trange
from astropy.io import fits
from astropy.wcs import WCS


def main(args):
    # Get path to patch.fits # patch.fitsまでのパスの取得
    # Inject artificial stars into only patch where forced_src.fits exists. # forced_srcが存在する領域にのみ人工星を埋め込む
    patch_path_list = []
    patch_list = []
    forced_path = args.path_to_rerun + "/deepCoadd-results/" + args.filter + "/" + str(args.tract) + "/*/" + "forced*.fits"
    for f in glob.glob(forced_path):
        patch = os.path.split(f)[1].replace("forced_src-" + args.filter + "-" + str(args.tract) + "-", "")
        patch_list.append(patch)
        patch_path_list.append(args.path_to_rerun+"/deepCoadd/"+args.filter+"/"+str(args.tract)+"/"+patch)

    # Main algorithm # メインのアルゴリズム
    for i in range(len(patch_path_list)):
        print("Start",patch_path_list[i])
        
        # Construction of PSF of the artificial star # 人工星のPSFの構築
        ## Load the patch information # patch.fitsの読み込み
        path_image = patch_path_list[i]# Path to the image (patch.fits)
        patch_hdul = fits.open(path_image)
        patch_img = patch_hdul[1].data
        img_wcs = WCS(patch_hdul[1].header)
        mask_img = patch_hdul[2].data
        mask_val = list(patch_hdul[2].header["MP_*"].values())
        
        ## Prepare teh array to contain artificial star information # 人工星の情報を保存する配列の用意
        star_Xpos = np.array([])
        star_Ypos = np.array([])
        star_Mag = np.array([])
        
        ## array for fake flag # fake flag 用の配列
        mask_array = np.full(patch_img.shape,0)
        
        ## write fake flag into header # fake flag を header に書き込む
        patch_hdul[2].header["MP_FAKE"] = np.max(mask_val) + 1
        
        ## Construct & inject the artificial star # 人工星の構築と注入
        injectMag  = args.mag
        exposure = afwImage.ExposureF(path_image)
        x0,y0 = exposure.getXY0() # Get where the origin of the patch image (i-th patch.fits; now we are looking) corresponds to in tract coordinates # 見ているパッチ画像の原点がtract座標上でどこに対応しているのかを取得
        injectPsf = exposure.getPsf()
        bin_size = 300# the pixel size of the artificial star [pixel]; the star to star distance # 構築する人工星のサイズ（人工星間の距離）
        x_len = int(np.floor(patch_img.shape[1]/bin_size))# Max number of artificial stars that can be injected laterally # 画像の横方向に注入できる人工星の最大数
        y_len = int(np.floor(patch_img.shape[0]/bin_size))# Max number of artificial stars that can be injected vertically # 画像の縦方向に注入できる人工星の最大数
        
        for j in range(x_len): 
            for k in range(y_len):
                try:  
                    xp = bin_size/2 + bin_size*j # X-coordinate on the patch image for which PSF is to be obtained; X-coordinates for injectiong the artificial star #  PSFを求めたいパッチ画像上でのx座標 = 人工星を埋め込みたいx座標
                    yp = bin_size/2 + bin_size*k  # Y-coordinate on the patch image for which PSF is to be obtained; Y-coordinates for injectiong the artificial star #  PSFを求めたいパッチ画像上でのy座標 = 人工星を埋め込みたいy座標
                    psfImage = injectPsf.computeImage(afwGeom.Point2D(xp+x0,yp+y0)) # Obtain the PSF at (xp,yp)
                    injected_star = psfImage.array
                    zeropoints = 27 # HSC zeropoints mag
                    n_times = 10**(-np.log10(np.sum(injected_star)) + (zeropoints-injectMag)/2.5)
                    injected_star = n_times * injected_star
                    
                    mask_pix = 5 # 人工星を埋めた場所にマスクをかける。マスクをかける領域の設定。 (5*5pix分マスクしている)
                    mask_array[int(xp)-int(mask_pix/2):int(xp)+int(1+mask_pix/2):,int(yp)-int(mask_pix/2):int(yp)+int(1+mask_pix/2)] = 2**(np.max(mask_val) + 1)
                    
                    if bin_size > injected_star.shape[1]:# x axis correction
                        diff_x = int(bin_size-injected_star.shape[1]) 
                        if diff_x%2 == 0: # 偶数の場合
                            injected_star = np.hstack([np.full([injected_star.shape[0],int(diff_x/2)],0), injected_star])
                            injected_star = np.hstack([injected_star, np.full([injected_star.shape[0],int(diff_x/2)],0)])
                        if diff_x%2 == 1: # 奇数の場合
                            injected_star = np.hstack([np.full([injected_star.shape[0],int(diff_x/2)],0), injected_star])
                            injected_star = np.hstack([injected_star, np.full([injected_star.shape[0],int(diff_x/2)+1],0)])
                    if bin_size > injected_star.shape[0]:
                        diff_y = int(bin_size-injected_star.shape[0])
                        if diff_y%2 == 0: # 偶数の場合
                            injected_star = np.vstack([np.full([int(diff_y/2),injected_star.shape[1]],0), injected_star]) 
                            injected_star = np.vstack([injected_star, np.full([int(diff_y/2),injected_star.shape[1]],0)]) 
                        if diff_y%2 == 1: # 奇数の場合
                            injected_star = np.vstack([np.full([int(diff_y/2),injected_star.shape[1]],0), injected_star]) 
                            injected_star = np.vstack([injected_star, np.full([int(diff_y/2)+1,injected_star.shape[1]],0)]) 
                    patch_img[bin_size*k:bin_size*k+bin_size,bin_size*j:bin_size*j+bin_size] += injected_star
                    star_Xpos = np.append(star_Xpos, img_wcs.wcs_pix2world(xp,yp,0)[0])
                    star_Ypos = np.append(star_Ypos, img_wcs.wcs_pix2world(xp,yp,0)[1])
                    star_Mag = np.append(star_Mag, injectMag)
                    print('Successful injection of the artificial star at ({:.1f},{:.1f})'.format(j,k))
                except lsst.pex.exceptions.wrappers.InvalidParameterError: 
                    print('Non-PSF at ({:.1f},{:.1f})'.format(j,k))
        mask_img += mask_array
        artificialCatalog = np.vstack([star_Xpos,star_Ypos,star_Mag]).T 
        # Save data
        primary_hdu = patch_hdul[0]
        image_hdu1 = fits.ImageHDU(patch_img,patch_hdul[1].header)
        image_hdu2 = fits.ImageHDU(mask_img,patch_hdul[2].header)
        image_hdu3 = patch_hdul[3]
        HDUL = fits.HDUList([primary_hdu,image_hdu1,image_hdu2,image_hdu3])
        for l in range(len(patch_hdul)-4): 
            HDUL.append(patch_hdul[l+4])
        HDUL.writeto(patch_path_list[i],overwrite=True) 
        print("Mock data is saved at "+patch_path_list[i])
        np.savetxt(patch_path_list[i]+'.txt',artificialCatalog)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_rerun", type=str, help="Enter the path to rerun.")
    parser.add_argument("filter", type=str, help="Enter the kind of fileter.")
    parser.add_argument("tract", type=int, help="Enter the tract number to inject the artifitial star.")
    parser.add_argument("mag", type=float, help="Enter the magnitude of the artifitial star.")
    args = parser.parse_args()
    main(args)
