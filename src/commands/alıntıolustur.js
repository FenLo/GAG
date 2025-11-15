const { SlashCommandBuilder } = require('discord.js');
const { createCanvas, loadImage, registerFont } = require('canvas');
const path = require('path');
const { AttachmentBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('alıntıolustur')
        .setDescription('Seçilen kişi ve mesaj ile alıntı oluşturur')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Alıntılanacak kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('mesaj')
                .setDescription('Alıntılanacak mesaj')
                .setRequired(true)),
    async execute(interaction) {
        await interaction.deferReply();

        const member = interaction.options.getMember('member');
        const message = interaction.options.getString('mesaj');

        try {
            // Create canvas
            const canvas = createCanvas(800, 400);
            const ctx = canvas.getContext('2d');

            // Background
            ctx.fillStyle = '#36393f';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw user avatar
            try {
                const avatar = await loadImage(member.user.displayAvatarURL({ extension: 'png', size: 128 }));
                ctx.drawImage(avatar, 50, 50, 100, 100);
            } catch (err) {
                console.error('Avatar load error:', err);
            }

            // User name
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 32px Arial';
            ctx.fillText(member.displayName, 170, 90);

            // Quote text
            ctx.fillStyle = '#dcddde';
            ctx.font = '24px Arial';
            const words = message.split(' ');
            let line = '';
            let y = 180;
            
            for (let i = 0; i < words.length; i++) {
                const testLine = line + words[i] + ' ';
                const metrics = ctx.measureText(testLine);
                if (metrics.width > 700 && i > 0) {
                    ctx.fillText(line, 50, y);
                    line = words[i] + ' ';
                    y += 35;
                } else {
                    line = testLine;
                }
            }
            ctx.fillText(line, 50, y);

            // Create attachment
            const attachment = new AttachmentBuilder(canvas.toBuffer(), { name: 'quote.png' });
            await interaction.followUp({ files: [attachment] });
        } catch (error) {
            console.error('Quote creation error:', error);
            await interaction.followUp({ 
                content: '❌ Alıntı oluştururken bir hata oluştu.',
                ephemeral: true 
            });
        }
    }
};
