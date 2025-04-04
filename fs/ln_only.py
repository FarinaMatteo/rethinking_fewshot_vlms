import torch
import torch.nn.functional as F

from contextlib import nullcontext
from fs.utils.model_utils import trainable_norm_params
from fs.utils.eval_utils import tokenize_texts, cls_acc, evaluate


def train_epoch(clip_model, optimizer, scheduler, scaler, train_loader, tokenized_texts, count_iters, total_iters, args):
    clip_model.train()
    acc_train = 0
    tot_samples = 0
    loss_epoch = 0.

    text_context_manager = torch.no_grad if args.ln_modality == 'vision' else nullcontext
    vision_context_manager = torch.no_grad if args.ln_modality == 'text' else nullcontext

    for i, (images, target) in enumerate(train_loader):
        
        # move data to GPU
        images, target = images.cuda(), target.cuda()

        # get both text and image features
        # wrapping the forward pass in autocast
        with torch.amp.autocast('cuda', dtype=torch.float16):
            with text_context_manager():
                text_features = clip_model.encode_text(tokenized_texts)
            with vision_context_manager():
                image_features = clip_model.encode_image(images)
        
        # well, you know that clip normalizes the features
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # compute loss and backward with scaling
        cosine_similarity = clip_model.logit_scale.exp() * image_features @ text_features.t()
        loss = F.cross_entropy(cosine_similarity, target)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scheduler.step()
        optimizer.zero_grad()
        scaler.update()
        
        # compute accuracy and loss
        acc_train += cls_acc(cosine_similarity, target) * target.shape[0]
        loss_epoch += loss.item() * target.shape[0]
        tot_samples += target.shape[0]
        
        # check if we reached the total number of iterations
        count_iters += 1
        if count_iters == total_iters:
            break
        
    # print after each epoch
    if count_iters <= total_iters:
        acc_train /= tot_samples
        loss_epoch /= tot_samples
        current_lr = scheduler.get_last_lr()[0]
        print('[{}/{}] LR: {:.6f}, Acc: {:.4f}, Loss: {:.4f}'.format(
            count_iters, total_iters, current_lr, acc_train, loss_epoch
            )
        )

    return clip_model, count_iters



def run_ln_only(args, clip_model, logit_scale, dataset, train_loader, val_loader, test_loader):
    
    clip_model = clip_model.cuda().float()
    total_iters = args.n_iters * args.shots
    
    # train only layer-norm instances
    trainable_params = trainable_norm_params(
        clip_model, 
        modality=args.ln_modality, 
        vision_start=args.ln_vision_start, 
        text_start=args.ln_text_start
    )
    optimizer = torch.optim.AdamW(trainable_params, lr=args.lr, weight_decay=args.wd, betas=(0.9, 0.999))
    print(f"Using AdamW with lr={args.lr}, wd={args.wd}, betas=(0.9, 0.999).")
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, total_iters, eta_min=1e-6)
    
    # training 
    scaler = torch.amp.GradScaler('cuda')
    count_iters = 0

    # we only need to tokenize once
    tokenized_texts = tokenize_texts(template=dataset.template[0], classnames=dataset.classnames)

    # start training for a fixed number of gradient steps (total_iters)  
    while count_iters < total_iters:
        clip_model, count_iters = train_epoch(
            clip_model, 
            optimizer, 
            scheduler, 
            scaler, 
            train_loader, 
            tokenized_texts, 
            count_iters, 
            total_iters,
            args
        )

        if args.debug: break
        
    # evaluate on test sets after training
    if args.setting == "base2new":
        test_base_loader, test_new_loader = test_loader
        
        # evaluation on base classes
        acc_test_base = evaluate(
            clip_model, test_base_loader, template=dataset.template[0], classnames=dataset.test_classnames
        )
        print("**** Test-Base accuracy: {:.2f}. ****\n".format(acc_test_base))

        # evaluation on novel classes
        acc_test_novel = evaluate(
            clip_model, test_new_loader, template=dataset.template[0], classnames=dataset.test_new_classnames
        )
        print("**** Test-Novel accuracy: {:.2f}. ****\n".format(acc_test_novel))
        result = {"acc_test_base": acc_test_base, "acc_test_new": acc_test_novel}
    
    else:
        acc_test = evaluate(
            clip_model, test_loader, template=dataset.template[0], classnames=dataset.test_classnames
        )
        print("\n**** Final test accuracy (all categories): {:.2f}. ****\n".format(acc_test))
        result = {"acc_test": acc_test}

    return result